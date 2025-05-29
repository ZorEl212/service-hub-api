from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, EmailStr, Field

from models.attributes import Address


class CustomerCreate(BaseModel):
    full_name: str = Field(default="")

class CustomerUpdate(BaseModel):
    full_name: str = Field(default="")
    address: Optional[Address]

class CustomerRead(BaseModel):
    id: PydanticObjectId
    user_id: PydanticObjectId
    email: EmailStr
    full_name: str = Field(default="")
    address: Optional[Address] = None

