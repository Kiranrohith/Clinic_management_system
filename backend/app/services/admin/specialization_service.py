import logging
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.admin.specialization_repository import AdminSpecializationRepository
from app.schemas.admin.specialization import SpecializationCreateRequest, SpecializationResponse

logger = logging.getLogger("clinic.admin")


class AdminSpecializationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AdminSpecializationRepository(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    def create_specialization(
        self,
        payload: SpecializationCreateRequest,
        actor_user_id: int,
    ) -> SpecializationResponse:
        specialization_name = payload.specialization_name.strip()
        existing = self.repo.get_specialization_by_name(specialization_name)
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Specialization already exists.")
        specialization = self.repo.create_specialization(
            specialization_name=specialization_name,
            actor_user_id=actor_user_id,
            now=self._now(),
        )
        return SpecializationResponse(
            specialization_id=specialization.specialization_id,
            specialization_name=specialization.specialization_name,
        )

    def list_specializations(self) -> list[SpecializationResponse]:
        items = self.repo.list_specializations()
        return [
            SpecializationResponse(
                specialization_id=item.specialization_id,
                specialization_name=item.specialization_name,
            )
            for item in items
        ]
