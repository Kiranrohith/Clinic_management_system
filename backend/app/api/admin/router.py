from fastapi import APIRouter

from app.api.admin.dashboard_router import router as dashboard_router
from app.api.admin.user_router import router as user_router
from app.api.admin.specialization_router import router as specialization_router
from app.api.admin.slot_router import router as slot_router
from app.api.admin.clinic_router import router as clinic_router
from app.api.admin.patient_router import router as patient_router
from app.api.admin.contact_router import router as contact_router
from app.api.admin.profile_router import router as profile_router

router = APIRouter()
router.include_router(dashboard_router)
router.include_router(user_router)
router.include_router(specialization_router)
router.include_router(slot_router)
router.include_router(clinic_router)
router.include_router(patient_router)
router.include_router(contact_router)
router.include_router(profile_router)
