from datetime import date, datetime, time

from pydantic import BaseModel, Field

from app.models.enums import AppointmentStatus, Gender


class DoctorCancelAppointmentRequest(BaseModel):
    cancellation_reason: str = Field(min_length=1)


class DoctorPatientSummaryResponse(BaseModel):
    patient_id: int
    full_name: str
    phone: str
    gender: Gender | None
    dob: date | None
    age: int | None
    blood_group: str | None
    address: str | None
    emergency_contact: str | None


class DoctorAppointmentResponse(BaseModel):
    appointment_id: int
    patient_id: int
    patient_name: str
    patient_phone: str
    available_date: date
    slot_start_time: time
    slot_end_time: time
    appointment_status: AppointmentStatus
    booking_source: str | None
    cancellation_reason: str | None
    completed_at: datetime | None


class DoctorAppointmentDetailResponse(BaseModel):
    appointment_id: int
    patient: DoctorPatientSummaryResponse
    available_date: date
    slot_start_time: time
    slot_end_time: time
    appointment_status: AppointmentStatus
    booking_source: str | None
    cancellation_reason: str | None
    completed_at: datetime | None
    reason_for_visit: str | None
    can_edit_prescription: bool
    current_prescription: "DoctorPrescriptionResponse | None"
    previous_prescriptions: "list[DoctorPrescriptionHistoryItemResponse]"


# Forward references resolved at module level via TYPE_CHECKING pattern
# Imported here to avoid circular imports when used in DoctorAppointmentDetailResponse
from app.schemas.doctor.prescription import (  # noqa: E402
    DoctorPrescriptionResponse,
    DoctorPrescriptionHistoryItemResponse,
)

DoctorAppointmentDetailResponse.model_rebuild()
