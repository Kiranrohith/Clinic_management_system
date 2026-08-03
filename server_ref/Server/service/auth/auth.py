import bcrypt

from jose import jwt
from datetime import datetime, timedelta, UTC
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from engine.config import settings

from database.auth.auth import (
    create_auth_user,
    get_auth_user_by_email,
)

from schema.auth.auth import (
    SignUpRequestSchema,
    SignInRequestSchema,
)


class AuthService:

    def create_access_token(self, data: dict):
        data = data.copy()

        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        data.update({"exp": expire})

        return jwt.encode(
            data,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

    def get_auth_user_by_email(
        self,
        email: str,
        db: Session
    ):
        return get_auth_user_by_email(
            db,
            email
        )

    def signup(
        self,
        payload: SignUpRequestSchema,
        db: Session
    ):
        hashed_password = bcrypt.hashpw(
            payload.password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        return create_auth_user(
            db,
            payload,
            hashed_password
        )

    def signin(
        self,
        payload: SignInRequestSchema,
        db: Session
    ):
        user = get_auth_user_by_email(
            db,
            payload.email
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not bcrypt.checkpw(
            payload.password.encode("utf-8"),
            user.password.encode("utf-8")
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        access_token = self.create_access_token(
            {
                "sub": user.email
            }
        )

        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }

    def logout(self):
        return {
            "message": "Logout successful"
        }


auth_service = AuthService()