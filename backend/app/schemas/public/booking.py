from datetime import date, time

from pydantic import BaseModel, Field

from app.models.enums import Gender


class PublicBookingPatientInput(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=7, max_length=15)
    gender: Gender | None = None
    dob: date | None = None
    blood_group: str | None = Field(default=None, max_length=10)
    address: str | None = None
    emergency_contact: str | None = Field(default=None, max_length=15)


class PublicBookAppointmentRequest(BaseModel):
    availability_id: int
    patient: PublicBookingPatientInput


class PublicAuthenticatedBookAppointmentRequest(BaseModel):
    booking_session_token: str = Field(min_length=1)
    availability_id: int
    patient_phone: str = Field(min_length=7, max_length=15)
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
    phone: str = Field(min_length=7, max_length=15)


class PublicBookingOtpVerifyRequest(BaseModel):
    phone: str = Field(min_length=7, max_length=15)
    otp_code: str = Field(min_length=4, max_length=10)


class PublicBookingSessionResponse(BaseModel):
    booking_session_token: str
    expires_in_minutes: int
