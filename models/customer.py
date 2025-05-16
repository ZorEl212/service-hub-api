from datetime import datetime
from typing import List

from beanie import Document, Link
from pydantic import BaseModel as PydanticModel

from models.service import ServiceItem
from models.user import User
from models.attributes import Address


class History(PydanticModel):
    price: float
    services: Link[ServiceItem]
    status: str
    date: datetime


class Customer(Document):
    user_id: Link[User]
    first_name: str = ""
    last_name: str = ""
    username: str = ""
    address: Address
    saved_services: List[Link[ServiceItem]] = []
    history: List[History] = []


