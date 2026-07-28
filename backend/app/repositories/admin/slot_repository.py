from datetime import datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.schedule import DoctorAvailability, Slot


class AdminSlotRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_slot_by_time_range(self, start_time: time, end_time: time) -> Slot | None:
        stmt = select(Slot).where(
            Slot.slot_start_time == start_time,
            Slot.slot_end_time == end_time,
        )
        return self.db.execute(stmt).scalars().first()

    def create_slot(self, start_time: time, end_time: time, now: datetime) -> Slot:
        slot = Slot(slot_start_time=start_time, slot_end_time=end_time, created_at=now)
        self.db.add(slot)
        self.db.flush()
        return slot

    def bulk_create_slots(self, pairs: list[tuple[time, time]], now: datetime) -> list[Slot]:
        slots = []
        for start_time, end_time in pairs:
            existing = self.get_slot_by_time_range(start_time, end_time)
            if existing is None:
                slot = Slot(slot_start_time=start_time, slot_end_time=end_time, created_at=now)
                self.db.add(slot)
                slots.append(slot)
        self.db.flush()
        return slots

    def get_slot_by_id(self, slot_id: int) -> Slot | None:
        return self.db.execute(select(Slot).where(Slot.slot_id == slot_id)).scalar_one_or_none()

    def count_availabilities_for_slot(self, slot_id: int) -> int:
        stmt = select(DoctorAvailability).where(DoctorAvailability.slot_id == slot_id)
        return len(self.db.execute(stmt).scalars().all())

    def count_appointments_for_slot(self, slot_id: int) -> int:
        stmt = (
            select(Appointment)
            .join(DoctorAvailability, Appointment.availability_id == DoctorAvailability.availability_id)
            .where(DoctorAvailability.slot_id == slot_id)
        )
        return len(self.db.execute(stmt).scalars().all())

    def delete_availabilities_for_slot(self, slot_id: int) -> int:
        rows = list(
            self.db.execute(select(DoctorAvailability).where(DoctorAvailability.slot_id == slot_id)).scalars().all()
        )
        for row in rows:
            self.db.delete(row)
        self.db.flush()
        return len(rows)

    def delete_slot(self, slot: Slot) -> None:
        self.db.delete(slot)
        self.db.flush()

    def list_slots(self) -> list[Slot]:
        stmt = select(Slot).order_by(Slot.slot_start_time.asc())
        return list(self.db.execute(stmt).scalars().all())

    def delete_unreferenced_slots(self) -> int:
        referenced_ids = self.db.execute(
            select(DoctorAvailability.slot_id).distinct()
        ).scalars().all()
        stmt = select(Slot)
        if referenced_ids:
            stmt = stmt.where(Slot.slot_id.not_in(referenced_ids))
        unreferenced = list(self.db.execute(stmt).scalars().all())
        for slot in unreferenced:
            self.db.delete(slot)
        self.db.flush()
        return len(unreferenced)
