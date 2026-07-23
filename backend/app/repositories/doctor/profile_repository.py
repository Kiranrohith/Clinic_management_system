from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.doctor import Doctor, DoctorSpecialization, Specialization
from app.models.user import User


class DoctorProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_doctor_profile_row(self, doctor_user_id: int) -> tuple[User, Doctor] | None:
        stmt = (
            select(User, Doctor)
            .join(Doctor, Doctor.doctor_user_id == User.user_id)
            .where(User.user_id == doctor_user_id)
        )
        return self.db.execute(stmt).one_or_none()

    def get_doctor_for_update(self, doctor_user_id: int) -> Doctor | None:
        stmt = select(Doctor).where(Doctor.doctor_user_id == doctor_user_id).with_for_update()
        return self.db.execute(stmt).scalar_one_or_none()

    def save_doctor(self, doctor: Doctor) -> Doctor:
        self.db.add(doctor)
        self.db.flush()
        return doctor

    def list_doctor_specialization_names(self, doctor_user_id: int) -> list[str]:
        stmt = (
            select(Specialization.specialization_name)
            .join(DoctorSpecialization, DoctorSpecialization.specialization_id == Specialization.specialization_id)
            .where(DoctorSpecialization.doctor_user_id == doctor_user_id)
            .order_by(Specialization.specialization_name.asc())
        )
        return [str(item) for item in self.db.execute(stmt).scalars().all()]
