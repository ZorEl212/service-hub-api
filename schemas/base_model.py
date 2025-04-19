import datetime

from pydantic import BaseModel

class BaseAPIModel(BaseModel):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True  # Enables compatibility with FastAPI
