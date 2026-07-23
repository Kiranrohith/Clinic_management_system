import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import MANAGEMENT_ROLES
from app.core.jwt import create_access_token, create_refresh_token, decode_refresh_token
from app.core.security import hash_password, verify_password
from app.models.enums import UserStatus
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth.auth import TokenResponse, UserSummary

logger = logging.getLogger("clinic.auth")


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def login(self, email: str, password: str) -> TokenResponse:
        user = self.user_repository.get_by_email(email=email)
        if user is None:
            logger.warning("Login failed: unknown email %s", email)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
        if not verify_password(password, user.password_hash):
            logger.warning("Login failed: invalid password for %s", email)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive.")
        if user.role is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User role is not assigned.")
        role_name = user.role.role_name
        if role_name not in MANAGEMENT_ROLES:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User role is not allowed for management login.")
        token = create_access_token(subject=str(user.user_id), role=role_name)
        refresh_token = create_refresh_token(subject=str(user.user_id), role=role_name)
        logger.info("Login successful for user_id=%s role=%s", user.user_id, role_name)
        return TokenResponse(
            access_token=token,
            refresh_token=refresh_token,
            token_type=settings.access_token_type,
            user=self.get_user_summary(user),
        )

    @staticmethod
    def get_user_summary(user: User) -> UserSummary:
        return UserSummary(
            user_id=user.user_id,
            full_name=user.full_name,
            email=user.email,
            role_name=user.role.role_name,
        )

    def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect.")
        user.password_hash = hash_password(new_password)
        self.db.add(user)
        logger.info("Password changed for user_id=%s", user.user_id)

    def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_refresh_token(refresh_token)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
        try:
            numeric_user_id = int(user_id)
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject.") from exc
        user = self.user_repository.get_by_id(numeric_user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive.")
        if user.role is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User role is not assigned.")
        role_name = user.role.role_name
        if role_name not in MANAGEMENT_ROLES:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User role is not allowed for management login.")
        new_access_token = create_access_token(subject=str(user.user_id), role=role_name)
        new_refresh_token = create_refresh_token(subject=str(user.user_id), role=role_name)
        logger.info("Token refreshed for user_id=%s role=%s", user.user_id, role_name)
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type=settings.access_token_type,
            user=self.get_user_summary(user),
        )

    @staticmethod
    def logout(user: User) -> None:
        logger.info("Logout successful for user_id=%s role=%s", user.user_id, user.role.role_name)
