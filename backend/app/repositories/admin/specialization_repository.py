from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.doctor import Specialization


class AdminSpecializationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_specializations_by_ids(self, specialization_ids: list[int]) -> list[Specialization]:
        stmt = select(Specialization).where(Specialization.specialization_id.in_(specialization_ids))
        return list(self.db.execute(stmt).scalars().all())

    def get_specialization_by_name(self, specialization_name: str) -> Specialization | None:
        stmt = select(Specialization).where(Specialization.specialization_name == specialization_name)
        return self.db.execute(stmt).scalar_one_or_none()

    def create_specialization(
        self,
        specialization_name: str,
        actor_user_id: int,
        now: datetime,
    ) -> Specialization:
        specialization = Specialization(
            specialization_name=specialization_name,
            created_by=actor_user_id,
            updated_by=actor_user_id,
            created_at=now,
            updated_at=now,
        )
        self.db.add(specialization)
        self.db.flush()
        return specialization

    def list_specializations(self) -> list[Specialization]:
        stmt = select(Specialization).order_by(Specialization.specialization_name.asc())
        return list(self.db.execute(stmt).scalars().all())
