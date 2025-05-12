from typing import List, Optional, Annotated
from uuid import UUID

from fastapi_users import schemas
from pydantic import BaseModel, Field
from pydantic.types import StringConstraints

from schemas.base_model import BaseAPIModel

class CustomerCreate(BaseModel):
    first_name: str = Field(default="")
    last_name: str = Field(default="")
    username: str = Field(default="")
