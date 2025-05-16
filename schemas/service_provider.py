from typing import List, Optional, Annotated
from uuid import UUID

from beanie import PydanticObjectId
from pydantic import BaseModel, EmailStr
from pydantic.types import StringConstraints

from models.service_provider import Address
from schemas.base_model import BaseAPIModel

class ServiceProvider(BaseModel):
        user_id: PydanticObjectId
        name: str
        description: str
        categories: List[str]
        image: Optional[str]
        address: Optional[Address]
        phone: str
        website: Optional[str]
        hours: Optional[List[dict]]
        establishedYear: Optional[int]
        certifications: Optional[List[UUID]]
        insurance: Optional[UUID]
        licenseNumber: Optional[str]
        verified: Optional[bool]
        images: Optional[List[dict]]
        included: Optional[List[str]]
        excluded: Optional[List[str]]
        process: Optional[List[dict]]
        highlights: Optional[List[dict]]
        guarantees: Optional[List[dict]]
        faqs: Optional[List[dict]]
        availability: Optional[List[dict]]
        serviceRadius: Optional[str]
        serviceArea: Optional[str]
        serviceTypes: Optional[List[str]]

class ServiceProviderCreate(BaseModel):
    description: Annotated[str, StringConstraints(min_length=10, max_length=1000)]
    name: Annotated[str, StringConstraints(min_length=2, max_length=100)]
    phone: Annotated[str, StringConstraints(min_length=10, max_length=15)]
    website: Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^https?://.*")] | None
    categories: List[str]

class ServiceProviderUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    categories: Optional[List[str]]
    address: Optional[Address]
    hours: Optional[List[dict]]
    establishedYear: Optional[int]
    certifications: Optional[List[UUID]]
    insurance: Optional[UUID]
    licenseNumber: Optional[str]
    verified: Optional[bool]
    images: Optional[List[dict]]
    included: Optional[List[str]]
    excluded: Optional[List[str]]
    process: Optional[List[dict]]
    highlights: Optional[List[dict]]
    guarantees: Optional[List[dict]]
    faqs: Optional[List[dict]]


