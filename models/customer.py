from datetime import datetime
from typing import List, Optional

from beanie import Document, Link
from pydantic import BaseModel as PydanticModel

from models.service import ServiceItem
from models.user import User
from models.attributes import Address
from schemas.customer import CustomerRead


class History(PydanticModel):
    price: float
    services: Link[ServiceItem]
    status: str
    date: datetime


class Customer(Document):
    user_id: Link[User]
    full_name: str = ""
    address: Optional[Address] = None
    saved_providers: List[Link[ServiceItem]] = []
    history: List[History] = []

    async def to_read_model(self) -> CustomerRead:
        await self.fetch_all_links()
        return CustomerRead(
            id=self.id,
            user_id=self.user_id.id,
            email=self.user_id.email,
            full_name=self.full_name,
            address=self.address
        )
