from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.constants import ROLE_DOCTOR
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.user import User
from app.schemas.doctor.appointment import DoctorCancelAppointmentRequest
from app.schemas.doctor.prescription import DoctorPrescriptionUpsertRequest
from app.services.doctor.appointment_service import DoctorAppointmentService
from app.services.doctor.prescription_service import DoctorPrescriptionService

router = APIRouter(prefix="/api/v1/doctor", tags=["Doctor"])


def _json_response(status_code: int, message: str, data: Any | None = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"status_code": status_code, "message": message, "data": data})


@router.get("/appointments")
def list_appointments(
    available_date: date | None = None,
    appointment_status: str | None = None,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    try:
        result = DoctorAppointmentService(db).list_appointments(
            doctor_user_id=current_user.user_id,
            available_date=available_date,
            appointment_status=appointment_status,
        )
        return _json_response(status.HTTP_200_OK, "Doctor appointments fetched successfully.", result)
    except ValueError as exc:
        return _json_response(status.HTTP_400_BAD_REQUEST, str(exc))
    except Exception as exc:
        return _json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc))


@router.get("/appointments/{appointment_id}")
def get_appointment_detail(
    appointment_id: int,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    try:
        result = DoctorAppointmentService(db).get_appointment_detail(current_user.user_id, appointment_id)
        return _json_response(status.HTTP_200_OK, "Doctor appointment detail fetched successfully.", result.model_dump())
    except LookupError as exc:
        return _json_response(status.HTTP_404_NOT_FOUND, str(exc))
    except Exception as exc:
        return _json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc))


@router.post("/appointments/{appointment_id}/complete")
def complete_appointment(
    appointment_id: int,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    try:
        result = DoctorAppointmentService(db).complete_appointment(current_user.user_id, appointment_id)
        return _json_response(status.HTTP_200_OK, "Appointment marked as completed.", result)
    except LookupError as exc:
        return _json_response(status.HTTP_404_NOT_FOUND, str(exc))
    except ValueError as exc:
        return _json_response(status.HTTP_409_CONFLICT, str(exc))
    except Exception as exc:
        return _json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc))


@router.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(
    appointment_id: int,
    payload: DoctorCancelAppointmentRequest,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    try:
        result = DoctorAppointmentService(db).cancel_appointment(current_user.user_id, appointment_id, payload)
        return _json_response(status.HTTP_200_OK, "Appointment cancelled by doctor.", result)
    except LookupError as exc:
        return _json_response(status.HTTP_404_NOT_FOUND, str(exc))
    except ValueError as exc:
        return _json_response(status.HTTP_409_CONFLICT, str(exc))
    except Exception as exc:
        return _json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc))


@router.put("/appointments/{appointment_id}/prescription")
def upsert_prescription(
    appointment_id: int,
    payload: DoctorPrescriptionUpsertRequest,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    try:
        result = DoctorPrescriptionService(db).upsert_prescription(current_user.user_id, appointment_id, payload)
        return _json_response(status.HTTP_200_OK, "Prescription updated successfully.", result.model_dump())
    except LookupError as exc:
        return _json_response(status.HTTP_404_NOT_FOUND, str(exc))
    except ValueError as exc:
        return _json_response(status.HTTP_409_CONFLICT, str(exc))
    except Exception as exc:
        return _json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc))


@router.get("/appointments/{appointment_id}/prescription")
def get_prescription(
    appointment_id: int,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    try:
        result = DoctorPrescriptionService(db).get_prescription(current_user.user_id, appointment_id)
        return _json_response(status.HTTP_200_OK, "Prescription fetched successfully.", result.model_dump())
    except LookupError as exc:
        return _json_response(status.HTTP_404_NOT_FOUND, str(exc))
    except Exception as exc:
        return _json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc))
