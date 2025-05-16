import datetime
from typing import List

from beanie import PydanticObjectId
from pydantic import BaseModel as PydanticModel

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