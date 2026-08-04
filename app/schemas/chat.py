from pydantic import BaseModel
from typing import Optional, List
import datetime

class MessageCreate(BaseModel):
    receiver_id: int
    message_text: Optional[str] = None
    message_type: str = "chat" # chat, request, call
    call_duration: Optional[int] = None # in seconds (for calls)

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    message_text: Optional[str] = None
    message_type: str
    is_read: bool
    call_duration: Optional[int] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class ChatParticipant(BaseModel):
    id: int
    name: str
    gender: str
    age: int
    photo_url: Optional[str] = None
    is_online: bool

class ChatSummaryResponse(BaseModel):
    participant: ChatParticipant
    last_message: MessageResponse
    unread_count: int
