from pydantic import BaseModel
from typing import Optional
class UserCreateRequestSchema(BaseModel):
    name: str
    phone_number: str
    email: str
class UserUpdateRequestSchema(BaseModel):
    name: str
    phone_number: str
    email: str
class UserResponseSchema(BaseModel):
    id: str
    name: str
    phone_number: str
    email: str
    created_at: str
    created_by: Optional[str] = None
    updated_at: str
    updated_by: Optional[str] = None
    is_active: bool
    is_deleted: bool