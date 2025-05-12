from typing import Annotated, Literal, Optional

from pydantic import EmailStr, Field, StringConstraints
from fastapi_users import schemas

from schemas.base_model import BaseAPIModel
from schemas.customer import CustomerCreate
from schemas.service_provider import ServiceProviderCreate


class UserCreate(schemas.BaseUserCreate):
    role: Literal["customer", "provider"]
    customer_profile: Optional[CustomerCreate] = None
    provider_profile: Optional[ServiceProviderCreate] = None

class User(BaseAPIModel):
    email: EmailStr
    role: Literal["customer", "provider"]

class UserUpdate(schemas.BaseUserUpdate):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=6)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
