from datetime import date, time

from pydantic import BaseModel, Field, field_validator

from app.models.enums import Gender
from app.schemas.validators import PhoneNumberStr, validate_dob_before_today


class PublicBookingPatientInput(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: PhoneNumberStr
    gender: Gender | None = None
    dob: date | None = None
    blood_group: str | None = Field(default=None, max_length=10)
    address: str | None = None
    emergency_contact: str | None = Field(default=None, max_length=15)

    @field_validator("dob")
    @classmethod
    def validate_dob(cls, value: date | None) -> date | None:
        return validate_dob_before_today(value)


class PublicBookAppointmentRequest(BaseModel):
    availability_id: int
    patient: PublicBookingPatientInput


class PublicAuthenticatedBookAppointmentRequest(BaseModel):
    booking_session_token: str = Field(min_length=1)
    availability_id: int
    patient_phone: PhoneNumberStr
    patient: PublicBookingPatientInput | None = None


class PublicBookAppointmentResponse(BaseModel):
    appointment_id: int
    patient_id: int
    availability_id: int
    appointment_status: str
    booking_source: str


class PublicJoinWaitingListRequest(BaseModel):
    availability_id: int
    patient: PublicBookingPatientInput


class PublicJoinWaitingListResponse(BaseModel):
    waiting_id: int
    patient_id: int
    availability_id: int
    position: int
    status: str


class PublicAppointmentCancelRequest(BaseModel):
    booking_session_token: str = Field(min_length=1)
    cancellation_reason: str = Field(min_length=1)


class PublicAppointmentRescheduleRequest(BaseModel):
    booking_session_token: str = Field(min_length=1)
    new_availability_id: int


class PublicAppointmentHistoryItemResponse(BaseModel):
    appointment_id: int
    patient_id: int
    patient_name: str
    patient_phone: str
    doctor_user_id: int
    doctor_name: str
    availability_id: int
    available_date: date
    slot_start_time: time
    slot_end_time: time
    appointment_status: str
    booking_source: str | None
    cancellation_reason: str | None
    completed_at: str | None
    created_at: str | None
    updated_at: str | None


class PublicBookingOtpRequest(BaseModel):
    phone: PhoneNumberStr


class PublicBookingOtpVerifyRequest(BaseModel):
    phone: PhoneNumberStr
    otp_code: str = Field(min_length=4, max_length=10)


class PublicBookingSessionResponse(BaseModel):
    booking_session_token: str
    expires_in_minutes: int
