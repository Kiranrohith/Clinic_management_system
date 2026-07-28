from datetime import time

from pydantic import BaseModel, EmailStr, Field

from app.schemas.validators import PhoneNumberStr


class ClinicSettingsUpsertRequest(BaseModel):
    clinic_name: str = Field(min_length=2, max_length=150)
    clinic_phone: PhoneNumberStr | None = None
    clinic_email: EmailStr | None = None
    clinic_address: str | None = None
    opening_time: time
    closing_time: time
    slot_duration_minutes: int = Field(ge=1, le=240)
    booking_window_days: int = Field(default=5, ge=1, le=90)
    appointment_limit_per_day: int = Field(default=2, ge=1, le=100)
    morning_break_start: time | None = None
    morning_break_end: time | None = None
    lunch_break_start: time | None = None
    lunch_break_end: time | None = None
    evening_break_start: time | None = None
    evening_break_end: time | None = None
    slot_generation_done: bool = False


class ClinicSettingsResponse(BaseModel):
    id: int
    clinic_name: str
    clinic_phone: str | None
    clinic_email: EmailStr | None
    clinic_address: str | None
    opening_time: time
    closing_time: time
    slot_duration_minutes: int
    booking_window_days: int
    appointment_limit_per_day: int
    morning_break_start: time | None
    morning_break_end: time | None
    lunch_break_start: time | None
    lunch_break_end: time | None
    evening_break_start: time | None
    evening_break_end: time | None
    slot_generation_done: bool
