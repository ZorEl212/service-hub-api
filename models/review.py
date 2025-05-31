from typing import Dict, List, Optional
from uuid import UUID

from beanie import Link

from models.base_model import BaseModel
from models.customer import Customer
from models.service import ServiceItem
from models.service_provider import ServiceProvider
from models.user import User


class Review(BaseModel):
    service_id: Link[ServiceItem]
    provider_id: Link[ServiceProvider]
    user_id: Link[Customer]
    rating: float  # 1-5 stars
    message: str
    attachments: Optional[Dict[UUID, Dict[str, str | bool]]] = (
        {}
    )  # Similar to image_urls in ServiceItem
    helpful_count: int = 0
    helpful_users: List[Link[User]] = []  # Users who found this review helpful

    class Settings:
        collection = "reviews"

    async def to_read_model(self):
        await self.fetch_link(Review.service_id)
        await self.fetch_link(Review.user_id)
        customer = self.user_id
        await customer.fetch_link(Customer.user_id)
        return {
            "id": str(self.id),
            "service_id": str(self.service_id.id),
            "user": {
                "id": str(self.user_id.id),
                "email": customer.user_id.email,
            },
            "rating": self.rating,
            "message": self.message,
            "attachments": self.attachments,
            "helpful_count": self.helpful_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
