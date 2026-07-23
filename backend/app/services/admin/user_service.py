import logging
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import MANAGEMENT_ROLES, ROLE_DOCTOR
from app.core.security import hash_password
from app.models.enums import UserStatus
from app.models.user import User
from app.repositories.admin.user_repository import AdminUserRepository
from app.repositories.admin.specialization_repository import AdminSpecializationRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.admin.user import (
    DoctorProfileInput,
    ManagementUserCreateRequest,
    ManagementUserResponse,
    ManagementUserUpdateRequest,
    UserStatusUpdateRequest,
)

logger = logging.getLogger("clinic.admin")


class AdminUserService:
    def __init__(self, db: Session):
        self.db = db
        self.admin_user_repo = AdminUserRepository(db)
        self.specialization_repo = AdminSpecializationRepository(db)
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    def create_management_user(
        self,
        payload: ManagementUserCreateRequest,
        actor_user_id: int,
    ) -> ManagementUserResponse:
        role_name = payload.role_name
        if role_name not in MANAGEMENT_ROLES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid management role.")

        email = payload.email.strip().lower()
        if self.user_repository.get_by_email(email) is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User email already exists.")

        phone = payload.phone.strip() if payload.phone else None
        if phone and self.user_repository.get_by_phone(phone) is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User phone already exists.")

        role = self.role_repository.get_by_name(role_name)
        if role is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role does not exist in roles table.")

        now = self._now()
        user = User(
            role_id=role.role_id,
            full_name=payload.full_name.strip(),
            email=email,
            phone=phone,
            password_hash=hash_password(payload.password),
            status=UserStatus.ACTIVE,
            created_by=actor_user_id,
            updated_by=actor_user_id,
            created_at=now,
            updated_at=now,
        )
        created_user = self.user_repository.add(user)

        if role_name == ROLE_DOCTOR:
            if payload.doctor_profile is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Doctor profile is required for DOCTOR role.",
                )
            specialization_ids = payload.doctor_profile.specialization_ids
            if specialization_ids:
                specializations = self.specialization_repo.get_specializations_by_ids(specialization_ids)
                if len(specializations) != len(set(specialization_ids)):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="One or more specialization IDs are invalid.",
                    )
            self.admin_user_repo.create_doctor_profile(
                doctor_user_id=created_user.user_id,
                qualification=payload.doctor_profile.qualification,
                experience_years=payload.doctor_profile.experience_years,
                consultation_fee=payload.doctor_profile.consultation_fee,
                about=payload.doctor_profile.about,
                actor_user_id=actor_user_id,
                now=now,
            )
            if specialization_ids:
                self.admin_user_repo.create_doctor_specialization_links(
                    doctor_user_id=created_user.user_id,
                    specialization_ids=specialization_ids,
                    actor_user_id=actor_user_id,
                    now=now,
                )
        elif payload.doctor_profile is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctor profile is allowed only for DOCTOR role.",
            )

        logger.info("Management user created user_id=%s role=%s by admin_user_id=%s", created_user.user_id, role_name, actor_user_id)
        return self._to_response(created_user, role_name)

    def list_management_users(self) -> list[ManagementUserResponse]:
        users = self.user_repository.list_by_role_names(MANAGEMENT_ROLES)
        return [self._to_response(u, u.role.role_name) for u in users]

    def update_management_user(
        self,
        user_id: int,
        payload: ManagementUserUpdateRequest,
        actor_user_id: int,
    ) -> ManagementUserResponse:
        user = self.user_repository.get_by_id(user_id)
        if user is None or user.role.role_name not in MANAGEMENT_ROLES:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Management user not found.")
        new_phone = payload.phone.strip() if payload.phone else None
        if new_phone and new_phone != user.phone:
            conflict = self.user_repository.get_by_phone(new_phone)
            if conflict is not None and conflict.user_id != user_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already used by another user.")
        user.full_name = payload.full_name.strip()
        user.phone = new_phone
        user.updated_by = actor_user_id
        user.updated_at = self._now()
        self.user_repository.save(user)
        return self._to_response(user, user.role.role_name)

    def set_user_status(
        self,
        user_id: int,
        payload: UserStatusUpdateRequest,
        actor_user_id: int,
    ) -> ManagementUserResponse:
        user = self.user_repository.get_by_id(user_id)
        if user is None or user.role.role_name not in MANAGEMENT_ROLES:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Management user not found.")
        if user.user_id == actor_user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change your own account status.")
        user.status = UserStatus[payload.status]
        user.updated_by = actor_user_id
        user.updated_at = self._now()
        self.user_repository.save(user)
        return self._to_response(user, user.role.role_name)

    @staticmethod
    def _to_response(user: User, role_name: str) -> ManagementUserResponse:
        return ManagementUserResponse(
            user_id=user.user_id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            role_name=role_name,
            status=user.status.value,
            created_at=user.created_at.isoformat() if user.created_at else None,
        )
