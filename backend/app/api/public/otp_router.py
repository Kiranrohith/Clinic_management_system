from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.public.booking import (
    PublicBookingOtpRequest,
    PublicBookingOtpVerifyRequest,
)
from app.schemas.public.prescription import (
    PublicPrescriptionOtpRequest,
    PublicPrescriptionVerifyRequest,
)
from app.services.public.otp_service import PublicOTPService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/public", tags=["Public"])


@router.post("/prescriptions/request-otp")
def request_prescription_otp(payload: PublicPrescriptionOtpRequest, db: Session = Depends(get_db)):
    data = PublicOTPService(db).request_prescription_otp(payload)
    return success_response("OTP sent successfully.", data.model_dump())


@router.post("/prescriptions/verify-otp")
def verify_prescription_otp(payload: PublicPrescriptionVerifyRequest, db: Session = Depends(get_db)):
    data = PublicOTPService(db).verify_prescription_otp(payload)
    return success_response("Prescriptions fetched successfully.", [item.model_dump() for item in data])


@router.post("/bookings/request-otp")
def request_booking_otp(payload: PublicBookingOtpRequest, db: Session = Depends(get_db)):
    data = PublicOTPService(db).request_booking_otp(payload)
    return success_response("OTP sent successfully.", data.model_dump())


@router.post("/bookings/verify-otp")
def verify_booking_otp(payload: PublicBookingOtpVerifyRequest, db: Session = Depends(get_db)):
    data = PublicOTPService(db).verify_booking_otp(payload)
    return success_response("Booking session created successfully.", data.model_dump())
