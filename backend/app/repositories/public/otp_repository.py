from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.communication import OTPVerification
from app.models.enums import OTPPurpose, OTPStatus


class PublicOTPRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_otp_verification(self, otp: OTPVerification) -> OTPVerification:
        self.db.add(otp)
        self.db.flush()
        return otp

    def get_latest_pending_otp(self, phone: str, purpose: OTPPurpose) -> OTPVerification | None:
        stmt = (
            select(OTPVerification)
            .where(
                OTPVerification.phone == phone,
                OTPVerification.purpose == purpose,
                OTPVerification.status == OTPStatus.PENDING,
            )
            .order_by(OTPVerification.created_at.desc(), OTPVerification.otp_id.desc())
        )
        return self.db.execute(stmt).scalars().first()

    def save_otp_verification(self, otp: OTPVerification) -> OTPVerification:
        self.db.add(otp)
        self.db.flush()
        return otp
