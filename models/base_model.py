# models/base.py
import uuid
from datetime import datetime

from beanie import Document
from fastapi.encoders import jsonable_encoder
from pydantic import ConfigDict, Field

import models
from utils.misc import MiscUtils


class BaseModel(Document):
    model_config = ConfigDict(
        json_encoders={datetime: MiscUtils.datetime_to_gmt_str},
        populate_by_name=True,
    )

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    async def save(self):
        self.updated_at = datetime.utcnow()
        await models.storage.new(self)
        await models.storage.save()

    async def delete(self):
        await models.storage.delete(self)
        await models.storage.save()

    async def to_dict(self):
        return jsonable_encoder(self.model_dump())

    class Settings:
        use_state_management = True
