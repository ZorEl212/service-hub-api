from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from beanie import Link
from pydantic import BaseModel, Field

from models.base_model import BaseModel
from models.customer import Customer
from models.service_provider import ServiceProvider
from models.user import User


class MessageAttachment(BaseModel):
    """Model for message attachments"""

    id: UUID = Field(default_factory=uuid4)
    type: str  # e.g., 'image', 'file', 'audio'
    url: str
    name: Optional[str] = None
    size: Optional[int] = None
    mime_type: Optional[str] = None


class Message(BaseModel):
    """Model for messages"""
    sender_id: Link[User]
    receiver_id: Link[User]
    content: str
    attachments: List[MessageAttachment] = []
    read: bool = False
    read_at: Optional[datetime] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}

    async def to_read_model(self):
        await self.fetch_link(Message.sender_id)
        await self.fetch_link(Message.receiver_id)

        # Determine sender and receiver types
        sender_type = "customer" if self.sender_id.role == "customer" else "provider"
        receiver_type = (
            "customer" if self.receiver_id.role == "customer" else "provider"
        )

        return {
            "id": str(self.id),
            "sender": {
                "id": str(self.sender_id.id),
                "type": sender_type,
                "name": (
                    self.sender_id.name if hasattr(self.sender_id, "name") else None
                ),
            },
            "receiver": {
                "id": str(self.receiver_id.id),
                "type": receiver_type,
                "name": (
                    self.receiver_id.name if hasattr(self.receiver_id, "name") else None
                ),
            },
            "content": self.content,
            "is_read": self.read,
            "attachments": self.attachments,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
