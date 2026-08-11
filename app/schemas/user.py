from pydantic import BaseModel, EmailStr
from typing import Optional, List
import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool = False
    created_at: datetime.datetime
    last_active_at: datetime.datetime
    membership_status: str
    plan_type: Optional[str] = None
    remaining_contact_views: int
    remaining_messages: int
    remaining_call_time: int
    credits: int
    plan_validity: Optional[datetime.datetime] = None
    id_verification_status: str
    id_verification_document_url: Optional[str] = None
    id_verified_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class PlanUpgrade(BaseModel):
    plan_type: str # Silver, Gold, Platinum
    payment_status: str # Success, Failed (simulated)

class IDVerificationRequest(BaseModel):
    document_url: str
