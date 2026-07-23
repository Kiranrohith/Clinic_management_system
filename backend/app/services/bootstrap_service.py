from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import MANAGEMENT_ROLES, ROLE_ADMIN
from app.core.security import hash_password
from app.models.enums import UserStatus
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository


class BootstrapService:
    def __init__(self, db: Session):
        self.db = db
        self.role_repository = RoleRepository(db)
        self.user_repository = UserRepository(db)

    def ensure_management_roles(self) -> dict:
        created_roles: list[str] = []
        existing_roles: list[str] = []

        for role_name in MANAGEMENT_ROLES:
            role = self.role_repository.get_by_name(role_name)
            if role is None:
                self.role_repository.create(role_name)
                created_roles.append(role_name)
            else:
                existing_roles.append(role_name)

        return {"created_roles": created_roles, "existing_roles": existing_roles}

    def ensure_initial_admin(self) -> dict:
        required_values = {
            "bootstrap_admin_full_name": settings.bootstrap_admin_full_name,
            "bootstrap_admin_email": settings.bootstrap_admin_email,
            "bootstrap_admin_password": settings.bootstrap_admin_password,
        }
        missing_keys = [key for key, value in required_values.items() if not value or not value.strip()]
        if missing_keys:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing bootstrap settings: {', '.join(missing_keys)}",
            )

        email = settings.bootstrap_admin_email.strip().lower()
        existing = self.user_repository.get_by_email(email)
        if existing is not None:
            return {"created": False, "user_id": existing.user_id, "email": existing.email}

        admin_role = self.role_repository.get_by_name(ROLE_ADMIN)
        if admin_role is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ADMIN role does not exist. Seed roles first.",
            )

        now = datetime.now(UTC).replace(tzinfo=None)
        user = User(
            role_id=admin_role.role_id,
            full_name=settings.bootstrap_admin_full_name.strip(),
            phone=settings.bootstrap_admin_phone.strip() if settings.bootstrap_admin_phone else None,
            email=email,
            password_hash=hash_password(settings.bootstrap_admin_password),
            status=UserStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
        self.user_repository.add(user)
        return {"created": True, "user_id": user.user_id, "email": user.email}
