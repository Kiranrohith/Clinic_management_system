from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import ROLE_DOCTOR
from app.models.doctor import Doctor, DoctorSpecialization, Specialization
from app.models.enums import SlotStatus
from app.models.schedule import DoctorAvailability, Slot
from app.models.user import Role, User


class FrontdeskAvailabilityRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_doctor_rows(self) -> list[tuple[Doctor, User, int | None, str | None]]:
        stmt = (
            select(
                Doctor,
                User,
                DoctorSpecialization.specialization_id,
                Specialization.specialization_name,
            )
            .join(User, User.user_id == Doctor.doctor_user_id)
            .join(Role, Role.role_id == User.role_id)
            .outerjoin(
                DoctorSpecialization,
                DoctorSpecialization.doctor_user_id == Doctor.doctor_user_id,
            )
            .outerjoin(
                Specialization,
                Specialization.specialization_id == DoctorSpecialization.specialization_id,
            )
            .where(Role.role_name == ROLE_DOCTOR)
            .order_by(User.full_name.asc())
        )
        return list(self.db.execute(stmt).all())

    def list_available_rows(
        self,
        doctor_user_id: int | None,
        available_date: date | None,
    ) -> list[tuple[DoctorAvailability, Slot, User]]:
        stmt = (
            select(DoctorAvailability, Slot, User)
            .join(Slot, Slot.slot_id == DoctorAvailability.slot_id)
            .join(Doctor, Doctor.doctor_user_id == DoctorAvailability.doctor_user_id)
            .join(User, User.user_id == Doctor.doctor_user_id)
            .where(DoctorAvailability.slot_status == SlotStatus.AVAILABLE)
            .order_by(DoctorAvailability.available_date.asc(), Slot.slot_start_time.asc())
        )
        if doctor_user_id is not None:
            stmt = stmt.where(DoctorAvailability.doctor_user_id == doctor_user_id)
        if available_date is not None:
            stmt = stmt.where(DoctorAvailability.available_date == available_date)
        return list(self.db.execute(stmt).all())
