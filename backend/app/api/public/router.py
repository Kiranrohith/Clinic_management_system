from fastapi import APIRouter

from app.api.public.doctor_router import router as doctor_router
from app.api.public.booking_router import router as booking_router
from app.api.public.otp_router import router as otp_router
from app.api.public.contact_router import router as contact_router

router = APIRouter()
router.include_router(doctor_router)
router.include_router(booking_router)
router.include_router(otp_router)
router.include_router(contact_router)
