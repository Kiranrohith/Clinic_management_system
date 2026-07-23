from pydantic import BaseModel

from app.schemas.public.doctor import PublicAvailabilityResponse


class FrontdeskAvailabilityResponse(PublicAvailabilityResponse):
    pass


class FrontdeskDoctorOptionResponse(BaseModel):
    doctor_user_id: int
    doctor_name: str
    specializations: list[str]
