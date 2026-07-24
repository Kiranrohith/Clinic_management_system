from datetime import date, time

from pydantic import BaseModel, EmailStr

from app.models.enums import Gender


class PublicSpecializationResponse(BaseModel):
    specialization_id: int
    specialization_name: str


class PublicDoctorResponse(BaseModel):
    doctor_user_id: int
    full_name: str
    qualification: str | None
    experience_years: int | None
    consultation_fee: float | None
    about: str | None
    specialization_ids: list[int]
    specialization_names: list[str]


class PublicAvailabilityResponse(BaseModel):
    availability_id: int
    doctor_user_id: int
    doctor_name: str
    available_date: date
    slot_id: int
    slot_start_time: time
    slot_end_time: time
    slot_status: str


class PublicClinicSettingsResponse(BaseModel):
    clinic_name: str
    clinic_phone: str | None
    clinic_email: EmailStr | None
    clinic_address: str | None
    opening_time: time
    closing_time: time
