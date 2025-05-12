from typing import Dict, List, Optional
from beanie import Link
from beanie import Document

from models.base_model import BaseModel
from models.service import Service
from models.user import User


class Address(Document):
    street: str
    city: str
    state: str
    zip: str
    location: Dict


class Certification(BaseModel):
    name: str
    issuer: str
    valid_until: str  # e.g., "2025-12-31"

    class Settings:
        collection = "certifications"


class Insurance(BaseModel):
    provider: str
    policy_number: str
    coverage: str
    valid_until: str  # e.g., "2025-12-31"

    class Settings:
        collection = "insurances"


class ServiceProvider(Document):
    user_id: Optional[Link[User]] = None
    name: str
    description: str
    categories: List[str]
    image: Optional[str] = None
    address: Optional[Link[Address]] = None
    phone: str
    website: Optional[str] = None
    hours: Optional[List[dict]] = None
    establishedYear: Optional[int] = None
    certifications: Optional[List[Link[Certification]]] = None
    insurance: Optional[Link[Insurance]] = None
    licenseNumber: Optional[str] = None
    verified: Optional[bool] = None
    services: Optional[List[Link[Service]]] = None
    images: Optional[List[dict]] = None
    included: Optional[List[str]] = None
    excluded: Optional[List[str]] = None
    process: Optional[List[dict]] = None
    highlights: Optional[List[dict]] = None
    guarantees: Optional[List[dict]] = None
    faqs: Optional[List[dict]] = None
    availability: Optional[List[dict]] = None
    serviceRadius: Optional[str] = None
    serviceArea: Optional[str] = None
    serviceTypes: Optional[List[str]] = None