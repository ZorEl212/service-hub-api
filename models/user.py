from pydantic import EmailStr

from models.base_model import BaseModel
from schemas.user import UserCreate


class User(BaseModel):
    """User model that defines attributes and methods for user instances"""

    email: EmailStr
    password: str
    first_name: str = ""
    last_name: str = ""
    username: str = ""

    @classmethod
    def from_create(cls, user: UserCreate) -> "User":
        """Create a User instance from a UserCreate schema"""
        return cls(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            password=cls.hash_password(user.password),
        )

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash the password using a secure hashing algorithm"""
        # Replace with secure hashing like bcrypt
        return password
