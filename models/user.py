from pydantic import Field
from fastapi_users_db_beanie import BaseOAuthAccount

from models.base_model import BaseModel
from schemas.user import UserCreate

from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase

class OAuthAccount(BaseOAuthAccount):
    pass

class User(BeanieBaseUser, BaseModel):
    """User model that defines attributes and methods for user instances"""

    first_name: str = ""
    last_name: str = ""
    username: str = ""
    oauth_accounts: list[OAuthAccount] = Field(default_factory=list)

    @classmethod
    def from_create(cls, user: UserCreate) -> "User":
        """Create a User instance from a UserCreate schema"""
        return cls(
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
        )

