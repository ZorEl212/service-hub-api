import datetime
from typing import Dict, List, Optional
from uuid import UUID

from beanie import PydanticObjectId
from pydantic import BaseModel as PydanticModel
from pydantic import BaseModel
from bson import ObjectId

from schemas.base_model import BaseAPIModel


class CategoryCreate(PydanticModel):
    title: str
    description: str
    serviceTypes: List[str]


class CategoryUpdate(PydanticModel):
    title: str
    description: str
    serviceTypes: List[str]

class CategoryRead(PydanticModel):
    id: PydanticObjectId
    title: str
    description: str
    provider_id: PydanticObjectId
    serviceTypes: List[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True  # Enables compatibility with ORM models

class PublicCategoryRead(PydanticModel):
    id: PydanticObjectId
    title: str
    description: str
    serviceTypes: List[str]

    class Config:
        from_attributes = True  # Enables compatibility with ORM models
        extra = "ignore"  # Ignore extra fields not defined in the model

class CategorySync(PydanticModel):
    created: List[CategoryCreate]
    updated: List[CategoryCreate]
    deleted: List[CategoryCreate]  # or some appropriate schema if `Service` is a Beanie model

class ServiceItemCreate(PydanticModel):
    title: str
    description: str
    category_id: PydanticObjectId
    price: float
    status: str
    image_urls: Optional[Dict[str, Dict[str, str | bool]] | List[str]]
    featured: bool

class ServiceItemUpdate(PydanticModel):
    title: str
    description: str
    category_id: PydanticObjectId
    price: float
    status: str
    image_urls: Optional[Dict[str, Dict[str, str | bool]]]
    featured: bool

class ServiceItemRead(PydanticModel):
    id: PydanticObjectId
    title: str
    description: str
    category_id: PydanticObjectId
    price: float
    status: str
    image_urls: Optional[Dict[UUID, Dict[str, str | bool]]]
    featured: bool
    rating: float
    reviewCount: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True  # Enables compatibility with ORM models

class PublicServiceItemRead(PydanticModel):
    id: PydanticObjectId
    title: str
    description: str
    category_id: PydanticObjectId
    price: float
    status: str
    image_urls: Optional[Dict[UUID, Dict[str, str | bool]]]
    featured: bool
    rating: float
    reviewCount: int

    class Config:
        from_attributes = True  # Enables compatibility with ORM models
        extra = "ignore"  # Ignore extra fields not defined in the model

class ServiceItemProviderProjection(BaseModel):
    provider_id: PydanticObjectId