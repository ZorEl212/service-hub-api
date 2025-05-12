from typing import Optional, Type, Union
from beanie import Document, PydanticObjectId
import motor.motor_asyncio
from fastapi_users.db import BeanieUserDatabase

from models.customer import Customer
from models.engine.interface import AbstractStorageEngine
from models.service import Service, ServiceItem
from models.service_provider import Address, Certification, Insurance, ServiceProvider
# Example class registry (like your `classes`)
from models.user import User

classes = {"User": User, "ServiceProvider": ServiceProvider, "Customer": Customer,
           "Address": Address, "Certification": Certification, "Insurance": Insurance,
           "Service": Service, "ServiceItem": ServiceItem}  # Add other models as needed

class DBStorage(AbstractStorageEngine):
    """Implements the same interface as FileStorage but using Beanie ODM"""

    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
        self.db = self.client.get_database("servicehub_db")

    async def init_beanie(self):
        from beanie import init_beanie
        await init_beanie(database=self.db, document_models=list(classes.values()))

    async def all(self, cls: Union[Type[Document], str] = None):
        """Returns all documents, optionally filtered by class"""
        if cls is None:
            results = []
            for model in classes.values():
                results.extend(await model.find_all().to_list())
            return results
        if isinstance(cls, str):
            cls = classes.get(cls)
        return await cls.find_all().to_list()

    async def new(self, obj: Document):
        """Add (or update) an object in DB"""
        await obj.create()

    async def save(self):
        """No-op for Beanie since objects save themselves"""
        pass

    async def reload(self):
        """No-op for Beanie, handled at init"""
        await self.init_beanie()

    async def delete(self, obj: Document):
        """Deletes an object from DB"""
        await obj.delete()

    async def get(self, cls: Type[Document] | str, obj_id: str):
        """Get document by class and id"""
        if isinstance(cls, str) and not classes.get(cls):
            return None
        return await classes.get(cls).get(obj_id) if isinstance(cls, str) else await cls.get(obj_id)

    async def count(self, cls: Type[Document] = None):
        """Count number of documents, optionally by class"""
        if cls is None:
            total = 0
            for model in classes.values():
                total += await model.find_all().count()
            return total
        return await cls.find_all().count()

    async def close(self):
        """Optional: close the MongoDB connection"""
        self.client.close()

    async def get_user_db(self):
        yield BeanieUserDatabase(User)
