from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

class SignUpRequestSchema(BaseModel):
    email: str
    password: str
class SignUpResponseDataSchema(BaseModel):
    id: UUID
    email: str
    created_at: datetime
    created_by: Optional[str] = None
    updated_at: datetime
    updated_by: Optional[str] = None
    is_active: bool
    is_deleted: bool
class SignInRequestSchema(BaseModel):
    email: str
    password: str
class SignInResponseDataSchema(BaseModel):
    access_token: str
    token_type: str
class LogOutResponseSchema(BaseModel):
    message: str