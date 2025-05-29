from typing import Optional

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    attachments: Optional[dict] = None


class MessageCreate(MessageBase):
    receiver_id: str


class MessageRead(MessageBase):
    id: str
    sender: dict
    receiver: dict
    is_read: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ChatRoom(BaseModel):
    id: str
    participants: list[dict]
    last_message: Optional[MessageRead] = None
    unread_count: int = 0
