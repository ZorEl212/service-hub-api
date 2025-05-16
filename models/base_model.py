# models/base.py
import uuid
from datetime import datetime

from beanie import Document, Link
from fastapi.encoders import jsonable_encoder
from pydantic import ConfigDict, Field

import models
from utils.misc import MiscUtils


class BaseModel(Document):
    model_config = ConfigDict(
        json_encoders={datetime: MiscUtils.datetime_to_gmt_str},
        populate_by_name=True,
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    async def save(self):
        self.updated_at = datetime.utcnow()
        await models.storage.new(self)
        await models.storage.save()

    def update_from_dict(self, data: dict):
        """
        Update the fields of the ServiceProvider instance from a dictionary.
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    async def delete(self):
        await models.storage.delete(self)
        await models.storage.save()

    async def to_dict(self):
        return jsonable_encoder(self.model_dump())

    class Settings:
        use_state_management = True
