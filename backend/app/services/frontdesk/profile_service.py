import logging
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.frontdesk.profile import FrontdeskProfileResponse, FrontdeskProfileUpdateRequest

logger = logging.getLogger("clinic.frontdesk")


class FrontdeskProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    def get_profile(self, current_user: User) -> FrontdeskProfileResponse:
        return FrontdeskProfileResponse(
            user_id=current_user.user_id,
            full_name=current_user.full_name,
            email=current_user.email,
            phone=current_user.phone,
            role_name=current_user.role.role_name,
            status=current_user.status,
        )

    def update_profile(self, current_user_id: int, payload: FrontdeskProfileUpdateRequest) -> FrontdeskProfileResponse:
        user = self.user_repository.get_by_id(current_user_id)
        if user is None or user.role is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        normalized_phone = payload.phone.strip() if payload.phone else None
        if normalized_phone:
            existing_phone_user = self.user_repository.get_by_phone(normalized_phone)
            if existing_phone_user is not None and existing_phone_user.user_id != current_user_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already belongs to another user.")
        user.full_name = payload.full_name.strip()
        user.phone = normalized_phone
        user.updated_by = current_user_id
        user.updated_at = self._now()
        saved = self.user_repository.save(user)
        return FrontdeskProfileResponse(
            user_id=saved.user_id,
            full_name=saved.full_name,
            email=saved.email,
            phone=saved.phone,
            role_name=saved.role.role_name,
            status=saved.status,
        )
