from pydantic import BaseModel, Field


class SpecializationCreateRequest(BaseModel):
    specialization_name: str = Field(min_length=2, max_length=100)


class SpecializationResponse(BaseModel):
    specialization_id: int
    specialization_name: str
