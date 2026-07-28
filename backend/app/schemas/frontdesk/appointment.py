from datetime import date, datetime, time

from pydantic import BaseModel, Field

from app.schemas.validators import PhoneNumberStr


class FrontdeskBookAppointmentRequest(BaseModel):
    availability_id: int
    patient_phone: PhoneNumberStr


class FrontdeskAppointmentResponse(BaseModel):
    appointment_id: int
    patient_id: int
    availability_id: int
    appointment_status: str
    booking_source: str


class FrontdeskCancelAppointmentRequest(BaseModel):
    cancellation_reason: str = Field(min_length=1)


class FrontdeskAppointmentListItemResponse(BaseModel):
    appointment_id: int
    patient_id: int
    patient_name: str
    patient_phone: str
    doctor_user_id: int
    doctor_name: str
    availability_id: int
    appointment_date: date
    slot_start_time: time
    slot_end_time: time
    appointment_status: str
    booking_source: str | None
    cancellation_reason: str | None
    created_at: datetime | None
    updated_at: datetime | None
