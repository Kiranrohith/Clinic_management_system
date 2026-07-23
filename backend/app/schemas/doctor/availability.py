from datetime import date, time

from pydantic import BaseModel, Field

from app.models.enums import SlotStatus


class DoctorAvailabilityCreateRequest(BaseModel):
    available_date: date
    slot_id: int


class DoctorAvailabilityTimeWindowRequest(BaseModel):
    available_date: date
    start_time: time
    end_time: time


class DoctorAvailabilityCancelRequest(BaseModel):
    cancellation_reason: str = Field(min_length=1)


class DoctorAvailabilityResponse(BaseModel):
    availability_id: int
    available_date: date
    slot_id: int
    slot_start_time: time
    slot_end_time: time
    slot_status: SlotStatus
    cancellation_reason: str | None


class DoctorAvailabilityTimeWindowResponse(BaseModel):
    available_date: date
    start_time: time
    end_time: time
    enabled_count: int
    disabled_count: int
    skipped_booked_count: int


class DoctorSlotOptionResponse(BaseModel):
    slot_id: int
    slot_start_time: time
    slot_end_time: time


class DoctorEmergencyCancelRequest(BaseModel):
    available_date: date
    from_slot_id: int
    cancellation_reason: str = Field(min_length=1)


class DoctorEmergencyCancelResponse(BaseModel):
    available_date: date
    from_slot_id: int
    cancelled_availability_ids: list[int]
    cancelled_appointment_ids: list[int]
