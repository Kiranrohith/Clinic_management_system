from datetime import date, time

from pydantic import BaseModel, Field


class DoctorPrescriptionUpsertRequest(BaseModel):
    diagnosis: str | None = None
    medicines: str | None = None
    dosage: str | None = None
    frequency: str | None = None
    duration: str | None = Field(default=None, max_length=100)
    doctor_advice: str | None = None
    internal_notes: str | None = None
    follow_up_date: date | None = None


class DoctorPrescriptionResponse(BaseModel):
    prescription_id: int
    appointment_id: int
    patient_id: int
    doctor_user_id: int
    diagnosis: str | None
    medicines: str | None
    dosage: str | None
    frequency: str | None
    duration: str | None
    doctor_advice: str | None
    internal_notes: str | None
    follow_up_date: date | None
    follow_up_reminder_sent: bool


class DoctorPrescriptionHistoryItemResponse(BaseModel):
    prescription_id: int
    appointment_id: int
    appointment_date: date
    slot_start_time: time
    slot_end_time: time
    doctor_user_id: int
    doctor_name: str
    diagnosis: str | None
    medicines: str | None
    dosage: str | None
    frequency: str | None
    duration: str | None
    doctor_advice: str | None
    internal_notes: str | None
    follow_up_date: date | None
