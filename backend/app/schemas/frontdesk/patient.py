from datetime import date

from pydantic import BaseModel, field_validator

from app.models.enums import Gender
from app.schemas.validators import PhoneNumberStr, validate_dob_before_today


class FrontdeskPatientUpsertRequest(BaseModel):
    full_name: str
    phone: PhoneNumberStr
    gender: Gender | None = None
    dob: date | None = None
    blood_group: str | None = None
    address: str | None = None
    emergency_contact: str | None = None

    @field_validator("dob")
    @classmethod
    def validate_dob(cls, value: date | None) -> date | None:
        return validate_dob_before_today(value)


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
