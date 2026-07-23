from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ROLE_FRONTDESK
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.user import User
from app.schemas.frontdesk.appointment import (
    FrontdeskBookAppointmentRequest,
    FrontdeskCancelAppointmentRequest,
)
from app.services.frontdesk.appointment_service import FrontdeskAppointmentService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/frontdesk", tags=["Frontdesk"])


@router.get("/availabilities")
def list_availabilities(
    doctor_user_id: int | None = None,
    available_date: date | None = None,
    _: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = FrontdeskAppointmentService(db).list_availabilities(
        doctor_user_id=doctor_user_id,
        available_date=available_date,
    )
    return success_response("Availabilities fetched successfully.", [item.model_dump() for item in data])


@router.get("/appointments/today")
def list_today_appointments(
    doctor_user_id: int | None = None,
    _: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = FrontdeskAppointmentService(db).list_appointments(appointment_date=date.today(), doctor_user_id=doctor_user_id)
    return success_response("Today's appointments fetched successfully.", [item.model_dump() for item in data])


@router.get("/appointments")
def list_appointments(
    appointment_date: date,
    doctor_user_id: int | None = None,
    _: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = FrontdeskAppointmentService(db).list_appointments(appointment_date=appointment_date, doctor_user_id=doctor_user_id)
    return success_response("Appointments fetched successfully.", [item.model_dump() for item in data])


@router.get("/appointments/{appointment_id}")
def get_appointment(
    appointment_id: int,
    _: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = FrontdeskAppointmentService(db).get_appointment(appointment_id)
    return success_response("Appointment fetched successfully.", data.model_dump())


@router.post("/appointments/book")
def book_appointment(
    payload: FrontdeskBookAppointmentRequest,
    current_user: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = FrontdeskAppointmentService(db).book_appointment(payload, actor_user_id=current_user.user_id)
    return success_response("Appointment booked successfully.", data.model_dump())


@router.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(
    appointment_id: int,
    payload: FrontdeskCancelAppointmentRequest,
    current_user: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = FrontdeskAppointmentService(db).cancel_appointment(
        appointment_id=appointment_id,
        payload=payload,
        actor_user_id=current_user.user_id,
    )
    return success_response("Appointment cancelled successfully.", data.model_dump())
