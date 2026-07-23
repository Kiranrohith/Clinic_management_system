from datetime import date

from pydantic import BaseModel


class PatientListItemResponse(BaseModel):
    patient_id: int
    full_name: str
    phone: str
    gender: str | None
    dob: date | None
    blood_group: str | None
    appointment_count: int
    created_at: str | None
