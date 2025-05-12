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

    async def get(self, cls: Type[Document] | str, obj_id: PydanticObjectId):
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

    async def get_by_attr(self, cls: Type[Document], attr: str, value):
        """Get document by attribute"""
        if not hasattr(cls, attr):
            raise ValueError(f"Attribute {attr} does not exist in {cls.__name__}")
        return await cls.find(getattr(cls, attr) == value).to_list()

    async def get_by_reference(
            self,
            cls: Type[Document],
            reference_field: str,
            reference_id: Union[str, PydanticObjectId],
            fetch_links: bool = False
    ) -> Optional[Document]:
        """Get document by a reference (Link) field like `user_id`.

        :param cls: The document class to query (e.g., Customer)
        :param reference_field: The reference field name (e.g., "user_id")
        :param reference_id: The id to match (string or ObjectId)
        :param fetch_links: Whether to resolve linked documents
        :return: The first matching document or None
        """
        if isinstance(reference_id, str):
            reference_id = PydanticObjectId(reference_id)

        field = getattr(cls, reference_field)
        return await cls.find(field.id == reference_id, fetch_links=fetch_links).first_or_none()

    async def get_user_db(self):
        yield BeanieUserDatabase(User)
