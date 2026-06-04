"""
Schemas para User.
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    full_name: str = Field(..., min_length=2, max_length=255)
    role: str = "productor"
    organization: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    phone: Optional[str] = None
    full_name: Optional[str] = None
    organization: Optional[str] = None
    sms_notifications: Optional[bool] = None
    email_notifications: Optional[bool] = None
    whatsapp_notifications: Optional[bool] = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    sms_notifications: bool
    email_notifications: bool
    whatsapp_notifications: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
