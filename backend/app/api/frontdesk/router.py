from fastapi import APIRouter

from app.api.frontdesk.dashboard_router import router as dashboard_router
from app.api.frontdesk.patient_router import router as patient_router
from app.api.frontdesk.appointment_router import router as appointment_router
from app.api.frontdesk.walkin_router import router as walkin_router
from app.api.frontdesk.profile_router import router as profile_router
from app.api.frontdesk.contact_router import router as contact_router

router = APIRouter()
router.include_router(dashboard_router)
router.include_router(patient_router)
router.include_router(appointment_router)
router.include_router(walkin_router)
router.include_router(profile_router)
router.include_router(contact_router)
