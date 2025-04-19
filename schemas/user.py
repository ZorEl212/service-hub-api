from pydantic import BaseModel, EmailStr, Field

from schemas.base_model import BaseAPIModel


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    first_name: str = Field(default="")
    last_name: str = Field(default="")
    username: str = Field(default="")


class User(BaseAPIModel):
    email: EmailStr
    password: str = Field(min_length=6)
    first_name: str = Field(default="")
    last_name: str = Field(default="")
    username: str = Field(default="")
