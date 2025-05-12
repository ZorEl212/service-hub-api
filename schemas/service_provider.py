from typing import List, Optional, Annotated
from uuid import UUID

from beanie import PydanticObjectId
from pydantic import BaseModel, EmailStr
from pydantic.types import StringConstraints

from schemas.base_model import BaseAPIModel

class ServiceProvider(BaseModel):
    user_id: PydanticObjectId
    name: str
    description: str
    image: Optional[str]
    address: Optional[UUID]
    phone: str
    website: Optional[str]
    hours: Optional[List[dict]]
    establishedYear: Optional[int]
    certifications: Optional[List[UUID]]
    insurance: Optional[UUID]
    licenseNumber: Optional[str]
    services: Optional[List[UUID]]

class ServiceProviderCreate(BaseModel):
    description: Annotated[str, StringConstraints(min_length=10, max_length=1000)]
    name: Annotated[str, StringConstraints(min_length=2, max_length=100)]
    phone: Annotated[str, StringConstraints(min_length=10, max_length=15)]
    website: Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^https?://.*")] | None
    categories: List[str]
