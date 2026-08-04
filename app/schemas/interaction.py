from pydantic import BaseModel
from typing import Optional, List
import datetime
from app.schemas.profile import ProfileResponse

class InterestBase(BaseModel):
    receiver_id: int

class InterestCreate(InterestBase):
    pass

class InterestUpdate(BaseModel):
    status: str # Accepted, Declined

class InterestResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    status: str
    created_at: datetime.datetime
    sender_profile: Optional[ProfileResponse] = None
    receiver_profile: Optional[ProfileResponse] = None

    class Config:
        from_attributes = True

class ProfileVisitResponse(BaseModel):
    id: int
    visitor_id: int
    visited_id: int
    created_at: datetime.datetime
    visitor_profile: Optional[ProfileResponse] = None
    visited_profile: Optional[ProfileResponse] = None

    class Config:
        from_attributes = True

class ContactViewResponse(BaseModel):
    id: int
    viewer_id: int
    viewed_id: int
    created_at: datetime.datetime
    viewed_profile: Optional[ProfileResponse] = None

    class Config:
        from_attributes = True

class FavouriteCreate(BaseModel):
    favourited_id: int

class FavouriteResponse(BaseModel):
    id: int
    user_id: int
    favourited_id: int
    created_at: datetime.datetime
    favourited_profile: Optional[ProfileResponse] = None

    class Config:
        from_attributes = True

class NoteCreate(BaseModel):
    profile_id: int
    note_text: str

class NoteResponse(BaseModel):
    id: int
    user_id: int
    profile_id: int
    note_text: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class BlockCreate(BaseModel):
    blocked_id: int

class BlockResponse(BaseModel):
    id: int
    blocker_id: int
    blocked_id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class PassCreate(BaseModel):
    passed_id: int

class PassResponse(BaseModel):
    id: int
    passer_id: int
    passed_id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True
