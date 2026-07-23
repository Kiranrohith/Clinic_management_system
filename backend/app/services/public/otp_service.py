import logging
import random
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.jwt import create_public_booking_token, decode_public_booking_token
from app.models.communication import OTPVerification
from app.models.enums import OTPPurpose, OTPStatus
from app.repositories.public.otp_repository import PublicOTPRepository
from app.repositories.public.prescription_repository import PublicPrescriptionRepository
from app.schemas.public.prescription import PublicPrescriptionItemResponse, PublicPrescriptionOtpRequest, PublicPrescriptionOtpResponse, PublicPrescriptionVerifyRequest
from app.schemas.public.booking import (
    PublicBookingOtpRequest,
    PublicBookingOtpVerifyRequest,
    PublicBookingSessionResponse,
)

logger = logging.getLogger("clinic.public")


class PublicOTPService:
    def __init__(self, db: Session):
        self.db = db
        self.otp_repo = PublicOTPRepository(db)
        self.rx_repo = PublicPrescriptionRepository(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    @staticmethod
    def _generate_otp_code() -> str:
        return f"{random.randint(0, 999999):06d}"

    @staticmethod
    def _print_testing_otp(phone: str, otp_code: str, purpose: str) -> None:
        print(f"Generated OTP ({purpose}) for {phone}", flush=True)
        print(f"OTP: {otp_code}", flush=True)

    def request_booking_otp(self, payload: PublicBookingOtpRequest) -> PublicPrescriptionOtpResponse:
        now = self._now()
        otp_code = self._generate_otp_code()
        otp = OTPVerification(
            phone=payload.phone.strip(),
            otp_code=otp_code,
            attempt_count=0,
            purpose=OTPPurpose.BOOK_APPOINTMENT,
            status=OTPStatus.PENDING,
            expires_at=now.replace(microsecond=0) + timedelta(minutes=settings.public_otp_expire_minutes),
            created_at=now,
        )
        self.otp_repo.create_otp_verification(otp)
        logger.info("Booking OTP generated phone=%s otp_id=%s", otp.phone, otp.otp_id)
        self._print_testing_otp(otp.phone, otp_code, "BOOK_APPOINTMENT")
        return PublicPrescriptionOtpResponse(
            message="OTP generated successfully.",
            expires_in_minutes=settings.public_otp_expire_minutes,
            otp_preview=None,
        )

    def verify_booking_otp(self, payload: PublicBookingOtpVerifyRequest) -> PublicBookingSessionResponse:
        now = self._now()
        otp = self.otp_repo.get_latest_pending_otp(phone=payload.phone.strip(), purpose=OTPPurpose.BOOK_APPOINTMENT)
        if otp is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OTP not found. Request a new OTP.")
        if otp.expires_at is not None and otp.expires_at <= now:
            otp.status = OTPStatus.EXPIRED
            self.otp_repo.save_otp_verification(otp)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired.")
        if otp.otp_code != payload.otp_code.strip():
            otp.attempt_count = (otp.attempt_count or 0) + 1
            if otp.attempt_count >= settings.public_otp_max_attempts:
                otp.status = OTPStatus.EXPIRED
            self.otp_repo.save_otp_verification(otp)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP.")
        otp.status = OTPStatus.VERIFIED
        otp.verified_at = now
        self.otp_repo.save_otp_verification(otp)
        booking_session_token = create_public_booking_token(payload.phone.strip())
        return PublicBookingSessionResponse(
            booking_session_token=booking_session_token,
            expires_in_minutes=settings.public_booking_session_minutes,
        )

    def request_prescription_otp(self, payload: PublicPrescriptionOtpRequest) -> PublicPrescriptionOtpResponse:
        now = self._now()
        otp_code = self._generate_otp_code()
        otp = OTPVerification(
            phone=payload.phone.strip(),
            otp_code=otp_code,
            attempt_count=0,
            purpose=OTPPurpose.VIEW_PRESCRIPTION,
            status=OTPStatus.PENDING,
            expires_at=now.replace(microsecond=0) + timedelta(minutes=settings.public_otp_expire_minutes),
            created_at=now,
        )
        self.otp_repo.create_otp_verification(otp)
        logger.info("Prescription OTP generated phone=%s otp_id=%s", otp.phone, otp.otp_id)
        self._print_testing_otp(otp.phone, otp_code, "VIEW_PRESCRIPTION")
        return PublicPrescriptionOtpResponse(
            message="OTP generated successfully.",
            expires_in_minutes=settings.public_otp_expire_minutes,
            otp_preview=None,
        )

    def verify_prescription_otp(self, payload: PublicPrescriptionVerifyRequest) -> list[PublicPrescriptionItemResponse]:
        now = self._now()
        otp = self.otp_repo.get_latest_pending_otp(phone=payload.phone.strip(), purpose=OTPPurpose.VIEW_PRESCRIPTION)
        if otp is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OTP not found. Request a new OTP.")
        if otp.expires_at is not None and otp.expires_at <= now:
            otp.status = OTPStatus.EXPIRED
            self.otp_repo.save_otp_verification(otp)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired.")
        if otp.otp_code != payload.otp_code.strip():
            otp.attempt_count = (otp.attempt_count or 0) + 1
            if otp.attempt_count >= settings.public_otp_max_attempts:
                otp.status = OTPStatus.EXPIRED
            self.otp_repo.save_otp_verification(otp)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP.")
        otp.status = OTPStatus.VERIFIED
        otp.verified_at = now
        self.otp_repo.save_otp_verification(otp)
        rows = self.rx_repo.list_prescription_rows_by_phone(payload.phone.strip())
        return [
            PublicPrescriptionItemResponse(
                prescription_id=prescription.prescription_id,
                appointment_id=prescription.appointment_id,
                doctor_name=doctor.full_name,
                diagnosis=prescription.diagnosis,
                medicines=prescription.medicines,
                dosage=prescription.dosage,
                frequency=prescription.frequency,
                duration=prescription.duration,
                doctor_advice=prescription.doctor_advice,
                follow_up_date=prescription.follow_up_date,
                created_at=prescription.created_at.isoformat() if prescription.created_at else None,
            )
            for prescription, doctor in rows
        ]
