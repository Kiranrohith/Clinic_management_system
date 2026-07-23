from fastapi import APIRouter

from app.api.doctor.dashboard_router import router as dashboard_router
from app.api.doctor.availability_router import router as availability_router
from app.api.doctor.appointment_router import router as appointment_router
from app.api.doctor.walkin_router import router as walkin_router
from app.api.doctor.profile_router import router as profile_router

router = APIRouter()
router.include_router(dashboard_router)
router.include_router(availability_router)
router.include_router(appointment_router)
router.include_router(walkin_router)
router.include_router(profile_router)
