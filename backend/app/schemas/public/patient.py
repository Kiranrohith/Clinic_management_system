from datetime import date

from pydantic import BaseModel

from app.models.enums import Gender


class PublicPatientProfileResponse(BaseModel):
    patient_id: int
    full_name: str
    phone: str
    gender: Gender | None
    dob: date | None
    blood_group: str | None
    address: str | None
    emergency_contact: str | None
