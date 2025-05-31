from typing import Dict, List, Optional

from beanie import Link
from pydantic import field_validator
import models
from models.base_model import BaseModel
from models.user import User
from models.attributes import ALLOWED_SUBCATEGORIES, Address, BusinessCategory, Subcategory
from schemas.service_provider import ServiceProvider as ServiceProviderRead


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


class ServiceProvider(BaseModel):
    user_id: Optional[Link[User]] = None
    name: str
    description: str
    category: Dict[BusinessCategory, List[Subcategory]]
    profile_picture: Optional[str]
    address: Optional[Address] = None
    phone: str
    website: Optional[str] = None
    hours: Optional[List[dict]] = None
    establishedYear: Optional[int] = None
    certifications: Optional[List[Link[Certification]]] = None
    insurance: Optional[Link[Insurance]] = None
    licenseNumber: Optional[str] = None
    verified: Optional[bool] = None
    included: Optional[List[str]] = None
    excluded: Optional[List[str]] = None
    process: Optional[List[dict]] = None
    highlights: Optional[List[dict]] = None
    guarantees: Optional[List[dict]] = None
    faqs: Optional[List[dict]] = None
    availability: Optional[List[dict]] = None
    serviceRadius: Optional[str] = None
    serviceArea: Optional[str] = None
    averageRating: Optional[float] = None
    reviewCount: Optional[int] = None

    @classmethod
    @field_validator("category")
    def validate_category(cls, value: Dict[BusinessCategory, List[Subcategory]]):
        for category, subcategories in value.items():
            allowed = ALLOWED_SUBCATEGORIES.get(category, [])
            for sub in subcategories:
                if sub not in allowed:
                    raise ValueError(
                        f"Subcategory '{sub}' is not allowed under category '{category}'. "
                        f"Allowed: {[s.value for s in allowed]}"
                    )
        return value

    async def to_read_model(self) -> ServiceProviderRead:
        await self.fetch_all_links()
        return ServiceProviderRead(
            id=self.id,
            user_id=self.user_id.id,
            email_verified=self.user_id.is_verified,
            email=self.user_id.email,
            name=self.name,
            description=self.description,
            category=self.category,
            profile_picture=self.profile_picture,
            address=self.address,
            phone=self.phone,
            website=self.website,
            hours=self.hours,
            establishedYear=self.establishedYear,
            certifications = [cert.id for cert in self.certifications] if self.certifications else None,
            insurance = self.insurance.id if self.insurance else None,
            licenseNumber=self.licenseNumber,
            verified=self.verified,
            included=self.included,
            excluded=self.excluded,
            process=self.process,
            highlights=self.highlights,
            guarantees=self.guarantees,
            faqs=self.faqs,
            availability=self.availability,
            serviceRadius=self.serviceRadius,
            serviceArea=self.serviceArea,
            averageRating=self.averageRating,
        )

    async def index_document(self):
        es_doc = await models.storage.index_search_document(self)
        await models.es.client.index(index="service_providers_v2", id=str(self.id), document=es_doc.model_dump())

    @classmethod
    async def index_documents(cls, documents: List["ServiceProvider"]):
        docs = [await models.storage.index_search_document(doc) for doc in documents]
        await models.es.bulk_index("service_providers_v2", docs)

    async def get_price_range(self) -> tuple[str, list[float]]:
        service_items = await models.storage.get_by_reference(
            "ServiceItem", "provider_id", self.id, fetch_links=True, batch=True)
        prices = [s.price for s in service_items if s.price is not None]

        if not prices:
            return "$0", [0, 0]

        min_price = min(prices)
        max_price = max(prices)

        if min_price == max_price:
            price_str = f"${min_price:.2f}"
        else:
            price_str = f"${min_price:.0f}-${max_price:.0f}/hr"

        return price_str, [min_price, max_price]
