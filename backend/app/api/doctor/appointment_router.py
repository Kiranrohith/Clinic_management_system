from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ROLE_DOCTOR
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.user import User
from app.schemas.doctor.appointment import DoctorCancelAppointmentRequest
from app.schemas.doctor.prescription import DoctorPrescriptionUpsertRequest
from app.services.doctor.appointment_service import DoctorAppointmentService
from app.services.doctor.prescription_service import DoctorPrescriptionService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/doctor", tags=["Doctor"])


@router.get("/appointments")
def list_appointments(
    available_date: date | None = None,
    appointment_status: str | None = None,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    data = DoctorAppointmentService(db).list_appointments(
        doctor_user_id=current_user.user_id,
        available_date=available_date,
        appointment_status=appointment_status,
    )
    return success_response("Doctor appointments fetched successfully.", [item.model_dump() for item in data])


@router.get("/appointments/{appointment_id}")
def get_appointment_detail(
    appointment_id: int,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    data = DoctorAppointmentService(db).get_appointment_detail(current_user.user_id, appointment_id)
    return success_response("Doctor appointment detail fetched successfully.", data.model_dump())


@router.post("/appointments/{appointment_id}/complete")
def complete_appointment(
    appointment_id: int,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    data = DoctorAppointmentService(db).complete_appointment(current_user.user_id, appointment_id)
    return success_response("Appointment marked as completed.", data.model_dump())


@router.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(
    appointment_id: int,
    payload: DoctorCancelAppointmentRequest,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    data = DoctorAppointmentService(db).cancel_appointment(current_user.user_id, appointment_id, payload)
    return success_response("Appointment cancelled by doctor.", data.model_dump())


@router.put("/appointments/{appointment_id}/prescription")
def upsert_prescription(
    appointment_id: int,
    payload: DoctorPrescriptionUpsertRequest,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    data = DoctorPrescriptionService(db).upsert_prescription(current_user.user_id, appointment_id, payload)
    return success_response("Prescription saved successfully.", data.model_dump())


@router.get("/appointments/{appointment_id}/prescription")
def get_prescription(
    appointment_id: int,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    data = DoctorPrescriptionService(db).get_prescription(current_user.user_id, appointment_id)
    return success_response("Prescription fetched successfully.", data.model_dump())
