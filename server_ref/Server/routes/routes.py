from fastapi import APIRouter
from routes.auth.auth import router as auth_router
from routes.user.user import router as user_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router,
    prefix="/auth",
    tags=["Auth"]
)

api_router.include_router(
    user_router,
    prefix="/user",
    tags=["User"]
)