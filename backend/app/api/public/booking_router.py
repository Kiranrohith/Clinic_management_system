from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.public.booking import (
    PublicAppointmentCancelRequest,
    PublicAppointmentRescheduleRequest,
    PublicAuthenticatedBookAppointmentRequest,
    PublicBookAppointmentRequest,
    PublicJoinWaitingListRequest,
)
from app.services.public.booking_service import PublicBookingService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/public", tags=["Public"])


@router.post("/appointments/book")
def book_appointment(payload: PublicBookAppointmentRequest, db: Session = Depends(get_db)):
    data = PublicBookingService(db).book_appointment(payload)
    return success_response("Appointment booked successfully.", data.model_dump())


@router.post("/appointments/book-authenticated")
def authenticated_book_appointment(payload: PublicAuthenticatedBookAppointmentRequest, db: Session = Depends(get_db)):
    data = PublicBookingService(db).authenticated_book_appointment(payload)
    return success_response("Appointment booked successfully.", data.model_dump())


@router.get("/appointments/history")
def list_booking_history(booking_session_token: str, db: Session = Depends(get_db)):
    data = PublicBookingService(db).list_booking_history(booking_session_token=booking_session_token)
    return success_response("Booking history fetched successfully.", [item.model_dump() for item in data])


@router.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int, payload: PublicAppointmentCancelRequest, db: Session = Depends(get_db)):
    data = PublicBookingService(db).cancel_appointment(appointment_id=appointment_id, payload=payload)
    return success_response("Appointment cancelled successfully.", data.model_dump())


@router.post("/appointments/{appointment_id}/reschedule")
def reschedule_appointment(
    appointment_id: int,
    payload: PublicAppointmentRescheduleRequest,
    db: Session = Depends(get_db),
):
    data = PublicBookingService(db).reschedule_appointment(appointment_id=appointment_id, payload=payload)
    return success_response("Appointment rescheduled successfully.", data.model_dump())


@router.post("/waiting-list/join")
def join_waiting_list(payload: PublicJoinWaitingListRequest, db: Session = Depends(get_db)):
    data = PublicBookingService(db).join_waiting_list(payload)
    return success_response("Waiting list joined successfully.", data.model_dump())


@router.get("/bookings/patients/by-phone")
def get_patient_for_booking(
    booking_session_token: str,
    patient_phone: str,
    db: Session = Depends(get_db),
):
    data = PublicBookingService(db).get_patient_for_booking(
        booking_session_token=booking_session_token,
        patient_phone=patient_phone,
    )
    return success_response("Patient fetched successfully.", data.model_dump())
