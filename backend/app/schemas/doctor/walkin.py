from datetime import date

from pydantic import BaseModel

from app.models.enums import WalkInStatus


class DoctorWalkInResponse(BaseModel):
    token_id: int
    token_number: int
    token_date: date
    patient_id: int
    patient_name: str
    patient_phone: str
    status: WalkInStatus
    notes: str | None


class DoctorWalkInStatusUpdateRequest(BaseModel):
    status: WalkInStatus
    notes: str | None = None
