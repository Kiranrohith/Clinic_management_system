from datetime import date, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import SlotStatus
from app.models.schedule import DoctorAvailability, Slot


class DoctorAvailabilityRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_availability_rows(
        self,
        doctor_user_id: int,
        available_date: date | None,
    ) -> list[tuple[DoctorAvailability, Slot]]:
        stmt = (
            select(DoctorAvailability, Slot)
            .join(Slot, Slot.slot_id == DoctorAvailability.slot_id)
            .where(DoctorAvailability.doctor_user_id == doctor_user_id)
            .order_by(DoctorAvailability.available_date.asc(), Slot.slot_start_time.asc())
        )
        if available_date is not None:
            stmt = stmt.where(DoctorAvailability.available_date == available_date)
        return list(self.db.execute(stmt).all())

    def get_availability_conflict(
        self,
        doctor_user_id: int,
        available_date: date,
        slot_id: int,
    ) -> DoctorAvailability | None:
        stmt = select(DoctorAvailability).where(
            DoctorAvailability.doctor_user_id == doctor_user_id,
            DoctorAvailability.available_date == available_date,
            DoctorAvailability.slot_id == slot_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_availabilities_for_date(
        self,
        doctor_user_id: int,
        available_date: date,
    ) -> list[DoctorAvailability]:
        stmt = select(DoctorAvailability).where(
            DoctorAvailability.doctor_user_id == doctor_user_id,
            DoctorAvailability.available_date == available_date,
        )
        return list(self.db.execute(stmt).scalars().all())

    def list_availability_rows_from_slot(
        self,
        doctor_user_id: int,
        available_date: date,
        slot_start_time: time,
    ) -> list[tuple[DoctorAvailability, Slot]]:
        stmt = (
            select(DoctorAvailability, Slot)
            .join(Slot, Slot.slot_id == DoctorAvailability.slot_id)
            .where(
                DoctorAvailability.doctor_user_id == doctor_user_id,
                DoctorAvailability.available_date == available_date,
                Slot.slot_start_time >= slot_start_time,
            )
            .order_by(Slot.slot_start_time.asc())
        )
        return list(self.db.execute(stmt).all())

    def get_slot(self, slot_id: int) -> Slot | None:
        stmt = select(Slot).where(Slot.slot_id == slot_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_slots(self) -> list[Slot]:
        stmt = select(Slot).order_by(Slot.slot_start_time.asc(), Slot.slot_end_time.asc())
        return list(self.db.execute(stmt).scalars().all())

    def create_availability(self, availability: DoctorAvailability) -> DoctorAvailability:
        self.db.add(availability)
        self.db.flush()
        return availability

    def get_availability_for_update(
        self,
        availability_id: int,
        doctor_user_id: int,
    ) -> DoctorAvailability | None:
        stmt = (
            select(DoctorAvailability)
            .where(
                DoctorAvailability.availability_id == availability_id,
                DoctorAvailability.doctor_user_id == doctor_user_id,
            )
            .with_for_update()
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def save_availability(self, availability: DoctorAvailability) -> DoctorAvailability:
        self.db.add(availability)
        self.db.flush()
        return availability
