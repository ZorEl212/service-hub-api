from typing import Any, Dict, List, Optional, Annotated
from uuid import UUID

from beanie import PydanticObjectId
from pydantic import BaseModel, EmailStr, model_validator
from pydantic.types import StringConstraints

from models.attributes import BusinessCategory, Subcategory
from models.service_provider import Address


class ServiceProvider(BaseModel):
        id: PydanticObjectId
        user_id: PydanticObjectId
        email: EmailStr
        email_verified: bool
        name: str
        description: str
        category: Dict[BusinessCategory, List[Subcategory]]
        address: Optional[Address]
        phone: str
        website: Optional[str]
        hours: Optional[List[dict]]
        establishedYear: Optional[int]
        certifications: Optional[List[UUID]]
        insurance: Optional[UUID]
        licenseNumber: Optional[str]
        verified: Optional[bool]
        profile_picture: Optional[str]
        included: Optional[List[str]]
        excluded: Optional[List[str]]
        process: Optional[List[dict]]
        highlights: Optional[List[dict]]
        guarantees: Optional[List[dict]]
        faqs: Optional[List[dict]]
        availability: Optional[List[dict]]
        serviceRadius: Optional[str]
        serviceArea: Optional[str]
        averageRating: Optional[float]
        reviewCount: Optional[int] = None

class ServiceProviderCreate(BaseModel):
    description: Annotated[str, StringConstraints(min_length=10, max_length=1000)]
    name: Annotated[str, StringConstraints(min_length=2, max_length=100)]
    phone: Annotated[str, StringConstraints(min_length=10, max_length=15)]
    website: Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^https?://.*")] | None
    category: Dict[BusinessCategory, List[Subcategory]]

class ServiceProviderUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    address: Optional[Address]
    hours: Optional[List[dict]]
    establishedYear: Optional[int]
    certifications: Optional[List[UUID]]
    insurance: Optional[UUID]
    licenseNumber: Optional[str]
    verified: Optional[bool]
    included: Optional[List[str]]
    excluded: Optional[List[str]]
    process: Optional[List[dict]]
    highlights: Optional[List[dict]]
    guarantees: Optional[List[dict]]
    faqs: Optional[List[dict]]

class PublicServiceProviderRead(BaseModel):
    id: PydanticObjectId
    email: EmailStr
    name: str
    description: str
    category: Dict[BusinessCategory, List[Subcategory]]
    address: Optional[Address]
    phone: str
    website: Optional[str]
    hours: Optional[List[dict]]
    establishedYear: Optional[int]
    certifications: Optional[List[str]]
    insurance: Optional[str]
    licenseNumber: Optional[str]
    verified: Optional[bool]
    included: Optional[List[str]]
    excluded: Optional[List[str]]
    process: Optional[List[dict]]
    highlights: Optional[List[dict]]
    guarantees: Optional[List[dict]]
    establishedYear: Optional[int]
    profile_picture: Optional[str]
    faqs: Optional[List[dict]]
    reviewCount: Optional[int] = None
    serviceArea: Optional[str] = None
    serviceRadius: Optional[str] = None
    averageRating: Optional[float] = None

    @classmethod
    @model_validator(mode="before")
    def parse_inputs(cls, data: dict[str, Any]) -> dict[str, Any]:
        if data.get("certifications") is not None:
            data["certifications"] = [
                str(cert.name) if not isinstance(cert, str) else cert
                for cert in data.get("certifications", [])
            ]
        if data.get("insurance") is not None:
            insurance = data["insurance"]
            data["insurance"] = (
                str(insurance.provider) if not isinstance(insurance, str) else insurance
            )
        return data

    class Config:
        orm_mode = True  # Enables compatibility with ORM models
        extra = "ignore"  # Ignore extra fields not defined in the model

