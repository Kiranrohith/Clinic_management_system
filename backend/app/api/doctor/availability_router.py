from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ROLE_DOCTOR
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.user import User
from app.schemas.doctor.availability import (
    DoctorAvailabilityCancelRequest,
    DoctorAvailabilityCreateRequest,
    DoctorAvailabilityTimeWindowRequest,
    DoctorEmergencyCancelRequest,
)
from app.services.doctor.availability_service import DoctorAvailabilityService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/doctor", tags=["Doctor"])


@router.get("/availabilities")
def list_availabilities(
    available_date: date | None = None,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    data = DoctorAvailabilityService(db).list_availabilities(current_user.user_id, available_date=available_date)
    return success_response("Doctor availabilities fetched successfully.", [item.model_dump() for item in data])


@router.get("/slots")
def list_slots(
    _: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    data = DoctorAvailabilityService(db).list_slots()
    return success_response("Doctor slots fetched successfully.", [item.model_dump() for item in data])


@router.post("/availabilities")
def create_availability(
    payload: DoctorAvailabilityCreateRequest,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    data = DoctorAvailabilityService(db).create_availability(current_user.user_id, payload)
    return success_response("Doctor availability created successfully.", data.model_dump())


@router.post("/availabilities/time-window")
def apply_availability_time_window(
    payload: DoctorAvailabilityTimeWindowRequest,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    data = DoctorAvailabilityService(db).apply_availability_time_window(current_user.user_id, payload)
    return success_response("Doctor availability window applied successfully.", data.model_dump())


@router.post("/availabilities/{availability_id}/cancel")
def cancel_availability(
    availability_id: int,
    payload: DoctorAvailabilityCancelRequest,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    data = DoctorAvailabilityService(db).cancel_availability(current_user.user_id, availability_id, payload)
    return success_response("Doctor availability cancelled successfully.", data.model_dump())


@router.post("/availabilities/emergency-cancel")
def emergency_cancel_remaining(
    payload: DoctorEmergencyCancelRequest,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    data = DoctorAvailabilityService(db).emergency_cancel_remaining(current_user.user_id, payload)
    return success_response("Remaining slots cancelled successfully.", data.model_dump())
