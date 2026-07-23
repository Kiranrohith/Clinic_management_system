from datetime import date

from pydantic import BaseModel, Field


class PublicPrescriptionOtpRequest(BaseModel):
    phone: str = Field(min_length=7, max_length=15)


class PublicPrescriptionOtpResponse(BaseModel):
    message: str
    expires_in_minutes: int
    otp_preview: str | None = None


class PublicPrescriptionVerifyRequest(BaseModel):
    phone: str = Field(min_length=7, max_length=15)
    otp_code: str = Field(min_length=4, max_length=10)


class PublicPrescriptionItemResponse(BaseModel):
    prescription_id: int
    appointment_id: int
    doctor_name: str
    diagnosis: str | None
    medicines: str | None
    dosage: str | None
    frequency: str | None
    duration: str | None
    doctor_advice: str | None
    follow_up_date: date | None
    created_at: str | None
