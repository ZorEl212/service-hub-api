from uuid import UUID

from pydantic import BaseModel as PydanticModel
from typing import Any, Dict, List, Optional
from beanie import Link
from models.base_model import BaseModel
from models.service_provider import ServiceProvider
from schemas.service import CategoryRead, ServiceItemRead


class Category(BaseModel):
    provider_id: Link[ServiceProvider]
    service_items: List[Link["ServiceItem"]] = []
    title: str
    description: str
    serviceTypes: Optional[List[str]]  # Categories of service, e.g., "Landscaping", "Cleaning"

    async def to_read_model(self) -> "CategoryRead":
        await self.fetch_link(Category.provider_id)
        return CategoryRead(
            id=self.id,
            title=self.title,
            description=self.description,
            provider_id=self.provider_id.id,  # only the ID is included
            created_at=self.created_at,
            updated_at=self.updated_at,
            serviceTypes=self.serviceTypes,
        )
    class Settings:
        collection = "services"

class ServiceItem(BaseModel):
    category_id: Link[Category]
    provider_id: Link[ServiceProvider]
    title: str
    description: str
    price: float
    image_urls: Optional[Dict[UUID, Dict[str, str | bool]]] | Any
    featured: bool
    rating: float
    status: str
    reviewCount: int

    async def to_read_model(self) -> "ServiceItemRead":
        await self.fetch_link(ServiceItem.category_id)
        return ServiceItemRead(
            id=self.id,
            title=self.title,
            description=self.description,
            price=self.price,
            image_urls=self.image_urls,
            featured=self.featured,
            status=self.status,
            rating=self.rating,
            reviewCount=self.reviewCount,
            category_id=self.category_id.id,  # only the ID is included
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
