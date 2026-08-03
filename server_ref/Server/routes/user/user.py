from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from engine.database import get_db
from service.user.user import user_service
from schema.user.user import (
    UserCreateRequestSchema,
    UserUpdateRequestSchema,
)
from service.user.user import notifications
import asyncio
from sse_starlette.sse import EventSourceResponse
router = APIRouter()


@router.post("/create")
def create_user(
    payload: UserCreateRequestSchema,
    db: Session = Depends(get_db)
):
    try:
        existing_user = user_service.get_user_by_email(
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

        result = user_service.create_user(payload, db)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "status_code": status.HTTP_201_CREATED,
                "message": "User created successfully",
                "detail": {
                    "id": str(result.id),
                    "name": result.name,
                    "phone_number": result.phone_number,
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
                "message": "Failed to create user",
                "detail": str(error),
            },
        )


@router.get("/")
def get_users(db: Session = Depends(get_db)):
    try:
        result = user_service.get_users(db)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status_code": status.HTTP_200_OK,
                "message": "Users fetched successfully",
                "detail": [
                    {
                        "id": str(user.id),
                        "name": user.name,
                        "phone_number": user.phone_number,
                        "email": user.email,
                    }
                    for user in result
                ],
            },
        )

    except Exception as error:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Failed to fetch users",
                "detail": str(error),
            },
        )

@router.put("/{user_id}")
def update_user(
    user_id: str,
    payload: UserUpdateRequestSchema,
    db: Session = Depends(get_db)
):
    try:
        user = user_service.get_user_by_id(user_id, db)

        if not user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "User not found",
                },
            )
        result = user_service.update_user(
            user,
            payload,
            db
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status_code": status.HTTP_200_OK,
                "message": "User updated successfully",
                "detail": {
                    "id": str(result.id),
                    "name": result.name,
                    "phone_number": result.phone_number,
                    "email": result.email,
                },
            },
        )
    except Exception as error:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Failed to update user",
                "detail": str(error),
            },
        )

@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    try:
        user = user_service.get_user_by_id(user_id, db)
        if not user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "User not found",
                },
            )
        user_service.delete_user(user, db)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status_code": status.HTTP_200_OK,
                "message": "User deleted successfully",
            },
        )
    except Exception as error:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Failed to delete user",
                "detail": str(error),
            },
        )
    
@router.get("/events")
async def events():
    async def event_generator():
        previous = 0
        while True:
            if len(notifications) > previous:
                latest = notifications[-1]
                yield {
                    "event": "message",
                    "data": str(latest["count"])
                }
                previous = len(notifications)
            await asyncio.sleep(1)
    return EventSourceResponse(event_generator())