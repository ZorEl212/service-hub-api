from typing import Literal

from pydantic import Field
from fastapi_users_db_beanie import BaseOAuthAccount

from models.base_model import BaseModel

from fastapi_users.db import BeanieBaseUser

class OAuthAccount(BaseOAuthAccount):
    pass

class User(BeanieBaseUser, BaseModel):
    """User model that defines attributes and methods for user instances"""
    role: Literal["customer", "provider"]

    oauth_accounts: list[OAuthAccount] = Field(default_factory=list)
