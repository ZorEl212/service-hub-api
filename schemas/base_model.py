import datetime

from beanie import PydanticObjectId
from fastapi_users import schemas
from pydantic import BaseModel

class BaseAPIModel(schemas.BaseUser[PydanticObjectId]):
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True  # Enables compatibility with FastAPI
