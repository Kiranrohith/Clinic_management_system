import logging
from datetime import UTC, datetime, time, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.clinic import ClinicSetting
from app.models.schedule import Slot
from app.repositories.admin.slot_repository import AdminSlotRepository
from app.repositories.admin.clinic_repository import AdminClinicRepository
from app.schemas.admin.slot import SlotCreateRequest, SlotResponse

logger = logging.getLogger("clinic.admin")


class AdminSlotService:
    def __init__(self, db: Session):
        self.db = db
        self.slot_repo = AdminSlotRepository(db)
        self.clinic_repo = AdminClinicRepository(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    @staticmethod
    def _normalize_time(value: time) -> time:
        return value.replace(second=0, microsecond=0)

    def _build_schedule_pairs(self, settings: ClinicSetting) -> list[tuple[time, time]]:
        opening_time = self._normalize_time(settings.opening_time)
        closing_time = self._normalize_time(settings.closing_time)
        if opening_time >= closing_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Opening time must be before closing time.")
        if settings.slot_duration_minutes <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slot duration must be greater than zero.")

        breaks: list[tuple[datetime, datetime]] = []
        dummy = datetime(2000, 1, 1)

        def _break(start: time | None, end: time | None) -> None:
            if start and end:
                normalized_start = self._normalize_time(start)
                normalized_end = self._normalize_time(end)
                if normalized_start < normalized_end:
                    breaks.append((
                        datetime.combine(dummy.date(), normalized_start),
                        datetime.combine(dummy.date(), normalized_end),
                    ))

        _break(settings.morning_break_start, settings.morning_break_end)
        _break(settings.lunch_break_start, settings.lunch_break_end)
        _break(settings.evening_break_start, settings.evening_break_end)
        breaks.sort(key=lambda value: value[0])

        pairs: list[tuple[time, time]] = []
        seen_pairs: set[tuple[time, time]] = set()
        cursor = datetime.combine(dummy.date(), opening_time)
        closing = datetime.combine(dummy.date(), closing_time)
        duration_delta = timedelta(minutes=settings.slot_duration_minutes)

        while cursor + duration_delta <= closing:
            slot_end = cursor + duration_delta
            overlaps = any(cursor < break_end and slot_end > break_start for break_start, break_end in breaks)
            if not overlaps:
                pair = (cursor.time(), slot_end.time())
                if pair not in seen_pairs:
                    pairs.append(pair)
                    seen_pairs.add(pair)
                cursor = slot_end
                continue
            for break_start, break_end in breaks:
                if cursor < break_end and slot_end > break_start:
                    cursor = break_end
                    break

        return pairs

    @staticmethod
    def _dedupe_by_time_range(slot_rows: list[Slot]) -> list[Slot]:
        deduped: dict[tuple[time, time], Slot] = {}
        for slot in slot_rows:
            key = (
                slot.slot_start_time.replace(second=0, microsecond=0),
                slot.slot_end_time.replace(second=0, microsecond=0),
            )
            existing = deduped.get(key)
            if existing is None or slot.slot_id < existing.slot_id:
                deduped[key] = slot
        return sorted(
            deduped.values(),
            key=lambda item: (item.slot_start_time, item.slot_end_time, item.slot_id),
        )

    def create_slot(self, payload: SlotCreateRequest) -> SlotResponse:
        start_time = self._normalize_time(payload.slot_start_time)
        end_time = self._normalize_time(payload.slot_end_time)
        if start_time >= end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="slot_start_time must be earlier than slot_end_time.",
            )
        existing = self.slot_repo.get_slot_by_time_range(
            start_time=start_time,
            end_time=end_time,
        )
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slot already exists for the same time range.")
        slot = self.slot_repo.create_slot(
            start_time=start_time,
            end_time=end_time,
            now=self._now(),
        )
        return SlotResponse(slot_id=slot.slot_id, slot_start_time=slot.slot_start_time, slot_end_time=slot.slot_end_time)

    def list_slots(self) -> list[SlotResponse]:
        items = self.slot_repo.list_slots()
        settings = self.clinic_repo.get_clinic_settings()
        if (
            settings is not None
            and settings.opening_time < settings.closing_time
            and settings.slot_duration_minutes > 0
        ):
            expected_pairs = set(self._build_schedule_pairs(settings))
            if expected_pairs:
                items = [
                    item
                    for item in items
                    if (
                        item.slot_start_time.replace(second=0, microsecond=0),
                        item.slot_end_time.replace(second=0, microsecond=0),
                    ) in expected_pairs
                ]
        deduped_items = self._dedupe_by_time_range(items)
        return [SlotResponse(slot_id=s.slot_id, slot_start_time=s.slot_start_time, slot_end_time=s.slot_end_time) for s in deduped_items]

    def delete_slot(self, slot_id: int) -> None:
        slot = self.slot_repo.get_slot_by_id(slot_id)
        if slot is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found.")
        appointment_count = self.slot_repo.count_appointments_for_slot(slot_id)
        if appointment_count > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Slot {slot_id} ({slot.slot_start_time}-{slot.slot_end_time}) has "
                    f"{appointment_count} patient appointment(s) booked and cannot be deleted."
                ),
            )
        # No patient has booked this slot with any doctor, so it is safe to clear any
        # doctor-marked availability for it and remove the slot itself. Running slot
        # generation again will recreate it from the clinic schedule if still applicable.
        self.slot_repo.delete_availabilities_for_slot(slot_id)
        self.slot_repo.delete_slot(slot)

    def generate_slots(self) -> list[SlotResponse]:
        """Auto-generate slots from clinic settings, skipping break periods."""
        settings = self.clinic_repo.get_clinic_settings()
        if settings is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Clinic settings not configured. Save clinic settings first.",
            )
        pairs = self._build_schedule_pairs(settings)

        now = self._now()
        self.slot_repo.delete_unreferenced_slots()
        self.slot_repo.bulk_create_slots(pairs, now)
        return self.list_slots()
