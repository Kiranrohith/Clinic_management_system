from fastapi import APIRouter

from app.api.admin.router import router as admin_router
from app.api.auth.router import router as auth_router
from app.api.doctor.router import router as doctor_router
from app.api.frontdesk.router import router as frontdesk_router
from app.api.notifications.router import router as notifications_router
from app.api.public.router import router as public_router

api_router = APIRouter()
api_router.include_router(public_router)
api_router.include_router(auth_router)
api_router.include_router(admin_router)
api_router.include_router(frontdesk_router)
api_router.include_router(doctor_router)
api_router.include_router(notifications_router)
