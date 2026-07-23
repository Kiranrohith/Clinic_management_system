from datetime import date

from pydantic import BaseModel

from app.models.enums import Gender


class FrontdeskPatientUpsertRequest(BaseModel):
    full_name: str
    phone: str
    gender: Gender | None = None
    dob: date | None = None
    blood_group: str | None = None
    address: str | None = None
    emergency_contact: str | None = None


class FrontdeskPatientResponse(BaseModel):
    patient_id: int
    full_name: str
    phone: str
    gender: Gender | None
    dob: date | None
    blood_group: str | None
    address: str | None
    emergency_contact: str | None


class FrontdeskPatientSearchItemResponse(BaseModel):
    patient_id: int
    full_name: str
    phone: str
