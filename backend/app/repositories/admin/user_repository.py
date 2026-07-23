from datetime import datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.doctor import Doctor, DoctorSpecialization


class AdminUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_doctor_profile(
        self,
        doctor_user_id: int,
        qualification: str | None,
        experience_years: int | None,
        consultation_fee: float | None,
        about: str | None,
        actor_user_id: int,
        now: datetime,
    ) -> Doctor:
        doctor = Doctor(
            doctor_user_id=doctor_user_id,
            qualification=qualification,
            experience_years=experience_years,
            consultation_fee=consultation_fee,
            about=about,
            created_by=actor_user_id,
            updated_by=actor_user_id,
            created_at=now,
            updated_at=now,
        )
        self.db.add(doctor)
        self.db.flush()
        return doctor

    def create_doctor_specialization_links(
        self,
        doctor_user_id: int,
        specialization_ids: list[int],
        actor_user_id: int,
        now: datetime,
    ) -> None:
        for specialization_id in specialization_ids:
            link = DoctorSpecialization(
                doctor_user_id=doctor_user_id,
                specialization_id=specialization_id,
                created_by=actor_user_id,
                updated_by=actor_user_id,
                created_at=now,
                updated_at=now,
            )
            self.db.add(link)
        self.db.flush()
