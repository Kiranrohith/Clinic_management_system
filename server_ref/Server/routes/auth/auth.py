from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from engine.database import get_db
from schema.auth.auth import (
    SignUpRequestSchema,
    SignInRequestSchema,
)
from service.auth.auth import auth_service

router = APIRouter()


@router.post("/signup")
def signup(
    payload: SignUpRequestSchema,
    db: Session = Depends(get_db)
):
    try:
        existing_user = auth_service.get_auth_user_by_email(
            payload.email,
            db
        )

        if existing_user:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Email already exists"
                }
            )

        result = auth_service.signup(
            payload,
            db
        )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "status_code": status.HTTP_201_CREATED,
                "message": "User registered successfully",
                "detail": {
                    "id": str(result.id),
                    "email": result.email,
                    "created_at": str(result.created_at),
                    "created_by": result.created_by,
                    "updated_at": str(result.updated_at),
                    "updated_by": result.updated_by,
                    "is_active": result.is_active,
                    "is_deleted": result.is_deleted,
                },
            },
        )

    except Exception as error:
        db.rollback()

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Failed to register user",
                "detail": str(error),
            },
        )


@router.post("/signin")
def signin(
    payload: SignInRequestSchema,
    db: Session = Depends(get_db)
):
    try:
        result = auth_service.signin(
            payload,
            db
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status_code": status.HTTP_200_OK,
                "message": "Login successful",
                "detail": result,
            },
        )

    except Exception as error:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "message": str(error),
            },
        )


@router.post("/logout")
def logout():
    try:
        result = auth_service.logout()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status_code": status.HTTP_200_OK,
                "message": result["message"],
            },
        )

    except Exception as error:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(error),
            },
        )