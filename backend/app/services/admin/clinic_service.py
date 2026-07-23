import logging
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.clinic import ClinicSetting
from app.repositories.admin.clinic_repository import AdminClinicRepository
from app.schemas.admin.clinic import ClinicSettingsUpsertRequest, ClinicSettingsResponse

logger = logging.getLogger("clinic.admin")


class AdminClinicService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AdminClinicRepository(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    def upsert_clinic_settings(
        self,
        payload: ClinicSettingsUpsertRequest,
        actor_user_id: int,
    ) -> ClinicSettingsResponse:
        if payload.opening_time >= payload.closing_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="opening_time must be earlier than closing_time.",
            )
        now = self._now()
        settings = self.repo.get_clinic_settings()
        if settings is None:
            settings = ClinicSetting(id=1, created_by=actor_user_id, created_at=now)
        settings.clinic_name = payload.clinic_name
        settings.clinic_phone = payload.clinic_phone
        settings.clinic_email = payload.clinic_email
        settings.clinic_address = payload.clinic_address
        settings.opening_time = payload.opening_time
        settings.closing_time = payload.closing_time
        settings.slot_duration_minutes = payload.slot_duration_minutes
        settings.booking_window_days = payload.booking_window_days
        settings.appointment_limit_per_day = payload.appointment_limit_per_day
        settings.morning_break_start = payload.morning_break_start
        settings.morning_break_end = payload.morning_break_end
        settings.lunch_break_start = payload.lunch_break_start
        settings.lunch_break_end = payload.lunch_break_end
        settings.evening_break_start = payload.evening_break_start
        settings.evening_break_end = payload.evening_break_end
        settings.slot_generation_done = payload.slot_generation_done
        settings.updated_by = actor_user_id
        settings.updated_at = now
        saved = self.repo.save_clinic_settings(settings)
        return self._to_response(saved)

    def get_clinic_settings(self) -> ClinicSettingsResponse | None:
        settings = self.repo.get_clinic_settings()
        if settings is None:
            return None
        return self._to_response(settings)

    @staticmethod
    def _to_response(s: ClinicSetting) -> ClinicSettingsResponse:
        return ClinicSettingsResponse(
            id=s.id,
            clinic_name=s.clinic_name,
            clinic_phone=s.clinic_phone,
            clinic_email=s.clinic_email,
            clinic_address=s.clinic_address,
            opening_time=s.opening_time,
            closing_time=s.closing_time,
            slot_duration_minutes=s.slot_duration_minutes,
            booking_window_days=s.booking_window_days,
            appointment_limit_per_day=s.appointment_limit_per_day,
            morning_break_start=s.morning_break_start,
            morning_break_end=s.morning_break_end,
            lunch_break_start=s.lunch_break_start,
            lunch_break_end=s.lunch_break_end,
            evening_break_start=s.evening_break_start,
            evening_break_end=s.evening_break_end,
            slot_generation_done=s.slot_generation_done,
        )
