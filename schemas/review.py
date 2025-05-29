from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class ReviewBase(BaseModel):
    rating: float = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    message: str = Field(
        ..., min_length=10, max_length=1000, description="Review message"
    )


class ReviewCreate(ReviewBase):
    service_id: str
    attachments: Optional[Dict[UUID, Dict[str, str | bool]]] = {}


class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1, le=5)
    message: Optional[str] = Field(None, min_length=10, max_length=1000)
    attachments: Optional[Dict[UUID, Dict[str, str | bool]]] = None


class ReviewRead(ReviewBase):
    id: str
    service_id: str
    user: Dict
    attachments: Dict[UUID, Dict[str, str | bool]]
    helpful_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
