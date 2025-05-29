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

    @model_validator(mode="before")
    def validate_profiles(self) -> 'UserCreate':
        if self["role"] == "customer":
            if self.get("customer_profile") is None:
                raise ValueError("customer_profile is required when role is 'customer'")
            self["provider_profile"] = None  # ignore if provided
        elif self.get("role") == "provider":
            if self.get("provider_profile") is None:
                raise ValueError("provider_profile is required when role is 'provider'")
            self["customer_profile"] = None  # ignore if provided
        print(f"type: {type(self)}, data: {self}")
        return self

class User(BaseAPIModel):
    email: EmailStr
    role: Literal["customer", "provider"]

class UserUpdate(schemas.BaseUserUpdate):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=6)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
