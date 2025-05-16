from pydantic import BaseModel as PydanticModel
from typing import List, Optional
from beanie import Link
from models.base_model import BaseModel
from models.service_provider import ServiceProvider
from schemas.service import CategoryRead


class Service(BaseModel):
    provider_id: Link[ServiceProvider]
    title: str
    description: str
    serviceTypes: Optional[List[str]]  # Categories of service, e.g., "Landscaping", "Cleaning"

    async def to_read_model(self) -> "CategoryRead":
        await self.fetch_link(Service.provider_id)
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
    service_id: Link[Service]
    name: str
    description: str
    price: float
    image: Optional[str]
    rating: float
    reviewCount: int
