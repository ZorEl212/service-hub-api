from typing import Optional, Type, Union
from beanie import Document, PydanticObjectId
import motor.motor_asyncio
from fastapi_users.db import BeanieUserDatabase

from models.appointment import Appointment
from models.customer import Customer
from models.engine.interface import AbstractStorageEngine
from models.service import Service, ServiceItem
from models.service_provider import Address, Certification, Insurance, ServiceProvider
# Example class registry (like your `classes`)
from models.user import User

classes = {"User": User, "ServiceProvider": ServiceProvider, "Customer": Customer,
            "Certification": Certification, "Insurance": Insurance,
           "Service": Service, "ServiceItem": ServiceItem,
           "Appointment": Appointment}  # Add other models as needed

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
        result = cls.find(field.id == reference_id, fetch_links=fetch_links)
        return await result.first_or_none() if not batch else await result.to_list()

    async def index_search_document(self, provider: ServiceProvider) -> ServiceProviderSearchDoc:
        await provider.fetch_all_links()
        service_items = await ServiceItem.find(ServiceItem.provider_id.id == provider.id).to_list()
        categories = await Category.find(Category.provider_id.id == provider.id).to_list()

        doc = ServiceProviderSearchDoc(
            id=str(provider.id),
            name=provider.name,
            description=provider.description,
            phone=provider.phone,
            category_text=" ".join(
                [k.value + " " + " ".join([v.value for v in vs]) for k, vs in provider.category.items()]
            ) if provider.category else "",
            service_titles=[s.title for s in service_items],
            service_descriptions=[s.description for s in service_items],
            category_titles=[c.title for c in categories],
            category_descriptions=[c.description for c in categories],
        )
        return doc

    async def find_with_count(
        self,
        cls: Type[Document] | str,
        filter_: dict = None,
        sort: Optional[List[tuple]] = None,
        skip: int = 0,
        limit: int = 10,
        fetch_links: bool = False
    ) -> tuple[list[Document], int]:
        """
        Find documents with pagination and return total count.

        :param cls: The Beanie document class.
        :param filter_: A dictionary of query filters.
        :param sort: A list of (field, direction) tuples for sorting.
        :param skip: Number of documents to skip (pagination).
        :param limit: Max number of documents to return.
        :param fetch_links: Whether to fetch linked documents.
        :return: A tuple of (documents list, total count).
        """
        cls = classes.get(cls) if isinstance(cls, str) else cls
        cursor = cls.find(filter_ or {}, fetch_links=fetch_links)

        if sort:
            cursor = cursor.sort(sort)

        total = await cursor.count()
        results = await cursor.skip(skip).limit(limit).to_list()

        return results, total

    async def get_user_db(self):
        yield BeanieUserDatabase(User)
