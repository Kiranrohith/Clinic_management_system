from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.enums import WalkInStatus
from app.schemas.validators import PhoneNumberStr


class FrontdeskWalkInCreateRequest(BaseModel):
    doctor_user_id: int
    token_date: date
    patient_phone: PhoneNumberStr
    notes: str | None = None


class FrontdeskWalkInStatusUpdateRequest(BaseModel):
    status: WalkInStatus
    notes: str | None = None


class FrontdeskWalkInResponse(BaseModel):
    token_id: int
    token_number: int
    token_date: date
    patient_id: int
    doctor_user_id: int
    status: WalkInStatus
    notes: str | None


class FrontdeskWalkInListItemResponse(BaseModel):
    token_id: int
    token_number: int
    token_date: date
    patient_id: int
    patient_name: str
    patient_phone: str
    doctor_user_id: int
    doctor_name: str
    status: WalkInStatus
    notes: str | None
    created_at: datetime | None
    updated_at: datetime | None
