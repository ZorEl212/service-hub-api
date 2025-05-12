from pydantic import BaseModel as PydanticModel
from typing import List, Optional
from beanie import Link
from models.base_model import BaseModel

class ServiceItem(BaseModel):
    name: str
    description: str
    price: float
    image: Optional[str]
    rating: float
    reviewCount: int

class Service(BaseModel):
    title: str
    description: str
    serviceTypes: List[str]  # Categories of service, e.g., "Landscaping", "Cleaning"
    items: List[Link[ServiceItem]]  # Items offered under the service

    class Settings:
        collection = "services"
