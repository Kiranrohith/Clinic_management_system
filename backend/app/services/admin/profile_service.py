import logging
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.schemas.admin.profile import AdminProfileResponse, AdminProfileUpdateRequest

logger = logging.getLogger("clinic.admin")


class AdminProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    def get_admin_profile(self, admin_user_id: int) -> AdminProfileResponse:
        user = self.user_repository.get_by_id(admin_user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin user not found.")
        return AdminProfileResponse(
            user_id=user.user_id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            role_name=user.role.role_name,
        )

    def update_admin_profile(
        self,
        admin_user_id: int,
        payload: AdminProfileUpdateRequest,
    ) -> AdminProfileResponse:
        user = self.user_repository.get_by_id(admin_user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin user not found.")
        new_phone = payload.phone.strip() if payload.phone else None
        if new_phone and new_phone != user.phone:
            conflict = self.user_repository.get_by_phone(new_phone)
            if conflict is not None and conflict.user_id != admin_user_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already used by another user.")
        user.full_name = payload.full_name.strip()
        user.phone = new_phone
        user.updated_by = admin_user_id
        user.updated_at = self._now()
        self.user_repository.save(user)
        return AdminProfileResponse(
            user_id=user.user_id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            role_name=user.role.role_name,
        )
