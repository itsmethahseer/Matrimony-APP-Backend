from pydantic import BaseModel, EmailStr
from typing import Optional, List
import datetime

class UserBase(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class GoogleAuthRequest(BaseModel):
    email: str
    google_id: str
    name: Optional[str] = None
    photo_url: Optional[str] = None

class SendOTPRequest(BaseModel):
    phone_number: str

class VerifyOTPRequest(BaseModel):
    phone_number: str
    otp_code: str

class FirebasePhoneAuthRequest(BaseModel):
    id_token: str
    phone_number: str

class ForgotPasswordRequest(BaseModel):
    identifier: str # Email or Phone/WhatsApp number
    method: str = "email" # "email" or "whatsapp"

class ResetPasswordRequest(BaseModel):
    identifier: str
    reset_token: str # OTP or token
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    email: Optional[str] = None
    phone_number: Optional[str] = None
    google_id: Optional[str] = None
    auth_provider: Optional[str] = "email"
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
