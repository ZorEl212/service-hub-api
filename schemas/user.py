from typing import Optional

from pydantic import EmailStr, Field
from fastapi_users import schemas

from schemas.base_model import BaseAPIModel


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str = Field(min_length=6)
    first_name: str = Field(default="")
    last_name: str = Field(default="")
    username: str = Field(default="")


class User(BaseAPIModel):
    email: EmailStr
    first_name: str = Field(default="")
    last_name: str = Field(default="")
    username: str = Field(default="")

class UserUpdate(schemas.BaseUserUpdate):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=6)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
