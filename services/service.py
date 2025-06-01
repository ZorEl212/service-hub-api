import uuid
from traceback import print_exc
from typing import Dict, List, Optional, Set

from beanie import PydanticObjectId
from fastapi import UploadFile
from pymongo import DESCENDING

import models
from models import media_storage
from models.service import Category, ServiceItem
from models.service_provider import ServiceProvider
from models.user import User
from schemas.service import CategoryCreate, PublicCategoryRead, PublicServiceItemRead, ServiceItemCreate, \
    ServiceItemUpdate
from services.app import AppCRUD
from utils.exceptions import AppException
from utils.service_result import ServiceResult


class CategoryCRUD(AppCRUD):
    """
    Handles Create, Read, Update, and Delete (CRUD) operations for service categories.
    """

    async def sync_categories(self, incoming: List[CategoryCreate], user: User) -> ServiceResult:
        """
        Synchronize categories with the incoming list of category data.

        :param incoming: List of dictionaries containing category data.
        :param user: Authenticated user
        :return: A dictionary with lists of created, updated, and deleted categories.
        """

        provider = await self.db.get_by_reference(ServiceProvider, "user_id", user.id)
        if not provider:
            return ServiceResult(Exception())

        incoming_titles = {item.title for item in incoming}

        existing_categories = await self.db.all(Category)
        existing_map = {cat.title: cat for cat in existing_categories}

        created, updated, deleted = [], [], []

        for item in incoming:
            title = item.title
            if title in existing_map:
                existing = existing_map[title]
                item_dict = item.model_dump(mode="python")
                changes = {k: v for k, v in item_dict.items() if k != "_id" and getattr(existing, k, None) != v}
                if changes:
                    for key, value in changes.items():
                        setattr(existing, key, value)
                    updated.append(existing)
            else:
                new_cat = Category(provider_id=provider.id, **item.model_dump(mode="python"))
                created.append(new_cat)

        to_delete = [cat for cat in existing_categories if cat.title not in incoming_titles and not cat.service_items]
        for cat in to_delete:
            print(len(cat.service_items))
        if to_delete:
            await self.db.delete_by_filter(Category, Category.title, [cat.title for cat in to_delete])
            deleted.append(*to_delete)

        if created:
            await self.db.batch_save(Category, created)
        if updated:
            await self.db.batch_update(updated)

        result = {
            "created": created,
            "updated": updated,
            "deleted": deleted
        }
        return ServiceResult(result)

    async def get_all(self, user: User) -> ServiceResult:
        """
        Get all service categories for a user.

        :param user: The user whose categories are to be retrieved.
        :return: ServiceResult containing the list of categories or an error.
        """
        try:
            provider = await self.db.get_by_reference(ServiceProvider, "user_id", user.id)
            categories = await self.db.get_by_reference(Category, "provider_id", provider.id, batch=True)
            return ServiceResult(categories)
        except Exception as e:
            print_exc()
            return ServiceResult(AppException.GetItem())

    async def get_by_provider(self, provider_id: str) -> ServiceResult:
        """
        Get all service categories for a specific service provider.

        :param provider_id: The ID of the service provider.
        :return: ServiceResult containing the list of categories or an error.
        """
        try:
            provider = await self.db.get(ServiceProvider, PydanticObjectId(provider_id))
            if not provider:
                return ServiceResult(AppException.NotFound({"message": "Provider not found"}))

            categories = await self.db.get_by_reference(Category, "provider_id", provider.id, batch=True)
            public_categories = [PublicCategoryRead(**(await cat.to_read_model()).model_dump()) for cat in categories]
            return ServiceResult(public_categories)
        except Exception as e:
            print_exc()
            return ServiceResult(AppException.GetItem())

class ServiceItemCRUD(AppCRUD):
    """
    """

    async def create_service(self, data: ServiceItemCreate, files: List[UploadFile], user: User) -> ServiceResult:
        """
        Create a new service item.

        :param data: The data for the new service item.
        :param files: List of files associated with the service item.
        :return: ServiceResult containing the created service item or an error.
        """
        try:
            image_urls: Dict[str, Dict[str, str]] = {}
            provider = await self.db.get_by_reference(ServiceProvider, "user_id", user.id)
            category = await self.db.get(Category, PydanticObjectId(data.category_id))
            if not provider:
                return ServiceResult(AppException.NotFound("Provider not found"))

            if files:
                for file in files:
                    id = uuid.uuid4()
                    public_id = f"{provider.id}_{id}"
                    result = media_storage.upload(file, public_id)
                    image_urls[id] = {"public_id": public_id, "url": result["secure_url"]}

            service_item = ServiceItem(**data.model_dump(mode="python"), provider_id=provider.id,
                                       reviewCount=0, rating=0)
            service_item.category_id = category
            service_item.image_urls = image_urls
            await service_item.save()
            return ServiceResult(await service_item.to_read_model())
        except Exception as e:
            print_exc()
            return ServiceResult(AppException.CreateItem())

    async def increment_hit_counter(self, service_item_id: str) -> ServiceResult:
        """
        Increment the hit counter for a service item.

        :param service_item_id: The ID of the service item.
        :return: ServiceResult indicating success or failure.
        """
        try:
            service_item: ServiceItem = await self.db.get(ServiceItem, PydanticObjectId(service_item_id))
            if not service_item:
                return ServiceResult(AppException.NotFound({"message": "Service item not found"}))

            service_item.hits += 1
            await service_item.save()
            return ServiceResult(True)
        except Exception as e:
            print_exc()
            return ServiceResult(AppException.UpdateItem())

    async def get_all_public(self, provider_id: str) -> ServiceResult:
        """
        Get all public service items for a service provider.

        :param provider_id: The ID of the service provider.
        :return: ServiceResult containing the list of public service items or an error.
        """
        try:
            provider = await self.db.get(ServiceProvider, PydanticObjectId(provider_id), fetch_links=True)
            if not provider:
                return ServiceResult(AppException.NotFound({"message": "Provider not found"}))

            service_items = await self.db.get_by_reference(ServiceItem, "provider_id", provider.id, batch=True, fetch_links=True)
            public_items = [
                PublicServiceItemRead(
                    **(await item.to_read_model()).model_dump(),
                )
                for item in service_items
                if item.status == "active"
            ]
            return ServiceResult(public_items)
        except Exception as e:
            print_exc()
            return ServiceResult(AppException.GetItem())

    async def get_all(self, user: User) -> ServiceResult:
        """
        Get all service items for a service provider.

        :param user: The user whose service items are to be retrieved.
        :return: ServiceResult containing the list of service items or an error.
        """
        try:
            provider = await self.db.get_by_reference(ServiceProvider, "user_id", user.id)
            if not provider:
                return ServiceResult(AppException.NotFound({"message": "Provider not found"}))

            service_items = await self.db.get_by_reference(ServiceItem, "provider_id", provider.id, batch=True)
            return ServiceResult([await serviceItem.to_read_model() for serviceItem in service_items])
        except Exception as e:
            print_exc()
            return ServiceResult(AppException.GetItem({"message": "Failed to retrieve service items"}))

    async def get_by_id(self, service_item_id: str, user: User) -> ServiceResult:
        """
        Get a service item by its ID.

        :param service_item_id: The ID of the service item to retrieve.
        :param user: The user requesting the service item.
        :return: ServiceResult containing the service item or an error.
        """
        try:
            provider = await self.db.get_by_reference(ServiceProvider, "user_id", user.id)
            if not provider:
                return ServiceResult(AppException.NotFound({"message": "Provider not found"}))

            service_item = await self.db.get(ServiceItem, PydanticObjectId(service_item_id), fetch_links=True)
            if not service_item:
                return ServiceResult(AppException.NotFound({"message": "Service item not found"}))

            await service_item.fetch_link(ServiceItem.category_id)  # Make sure category_id is resolved
            if service_item.provider_id.id != provider.id:
                print(f"Unauthorized access attempt. Service item provider: {service_item.provider_id.id}, user provider: {provider.id}")
                return ServiceResult(AppException.GetItem())

            return ServiceResult(await service_item.to_read_model())
        except Exception as e:
            print_exc()
            return ServiceResult(AppException.GetItem())

    async def update_service(self, service_item_id: str, data: ServiceItemUpdate, user: User, files: Optional[List[UploadFile]]) -> ServiceResult:
        """
        Update an existing service item.

        :param service_item_id: The ID of the service item to update.
        :param data: The updated data for the service item.
        :param user: The user updating the service item.
        :return: ServiceResult containing the updated service item or an error.
        """
        try:
            provider = await self.db.get_by_reference(ServiceProvider, "user_id", user.id)
            if not provider:
                return ServiceResult(AppException.NotFound("Provider not found"))

            service_item: ServiceItem = await self.db.get(ServiceItem, PydanticObjectId(service_item_id), fetch_links=True)
            if not service_item:
                return ServiceResult(AppException.NotFound("Service item not found"))
            category = await self.db.get(Category, PydanticObjectId(data.category_id))
            service_item.category_id = category

            await service_item.fetch_link(ServiceItem.category_id)  # Make sure category_id is resolved
            if service_item.provider_id.id != provider.id:
                print(f"Unauthorized update attempt. Service item provider: {service_item.provider_id.id}, user provider: {provider.id}")
                return ServiceResult(AppException.GetItem())

            # Update fields
            for field, value in data.model_dump(mode="python").items():
                if field not in ["provider_id", "id", "_id", "category_id"]:
                    setattr(service_item, field, value)

            if files:
                print("Uploaded file")
                for file in files:
                    id = uuid.uuid4()
                    public_id = f"{provider.id}_{id}"
                    result = self.media_storage.upload(file, public_id)
                    optmized_url = self.media_storage.generate_optimized_url(public_id)
                    print(optmized_url)
                    service_item.image_urls[id] = {"public_id": public_id, "url": result["secure_url"]}
            await service_item.save()
            return ServiceResult(await service_item.to_read_model())
        except Exception as e:
            print_exc()
            return ServiceResult(AppException.UpdateItem())

    async def delete_service(self, service_id: str, user: User) -> ServiceResult:
        """
        Delete a service item by its ID.

        :param service_id: The ID of the service item to delete.
        :param user: The user deleting the service item.
        :return: ServiceResult indicating success or failure.
        """
        try:
            provider = await self.db.get_by_reference(ServiceProvider, "user_id", user.id)
            if not provider:
                return ServiceResult(AppException.NotFound("Provider not found"))

            service_item: ServiceItem = await self.db.get(ServiceItem, PydanticObjectId(service_id), fetch_links=True)
            if not service_item:
                return ServiceResult(AppException.NotFound("Service item not found"))

            if service_item.provider_id.id != provider.id:
                print(f"Unauthorized delete attempt. Service item provider: {service_item.provider_id.id}, user provider: {provider.id}")
                return ServiceResult(AppException.GetItem())

            result = await service_item.delete_obj()
            print(result)
            return ServiceResult(True)
        except Exception as e:
            print_exc()
            return ServiceResult(AppException.DeleteItem())

    async def duplicate_service(self, service_id: str, user: User) -> ServiceResult:
        """
        Duplicate a service item by its ID.

        :param service_id: The ID of the service item to duplicate.
        :param user: The user duplicating the service item.
        :return: ServiceResult containing the duplicated service item or an error.
        """
        try:
            provider = await self.db.get_by_reference(ServiceProvider, "user_id", user.id)
            if not provider:
                return ServiceResult(AppException.NotFound("Provider not found"))

            service_item: ServiceItem = await self.db.get(ServiceItem, PydanticObjectId(service_id), fetch_links=True)
            if not service_item:
                return ServiceResult(AppException.NotFound("Service item not found"))

            await service_item.fetch_link(ServiceItem.category_id)  # Make sure category_id is resolved
            if service_item.provider_id.id != provider.id:
                print(f"Unauthorized duplicate attempt. Service item provider: {service_item.provider_id.id}, user provider: {provider.id}")
                return ServiceResult(AppException.GetItem())

            # Create a new instance with the same data but different ID
            new_service_item = ServiceItem(**service_item.model_dump(mode="python"))
            new_service_item.id = PydanticObjectId()
            new_service_item.provider_id = provider
            new_service_item.category_id = service_item.category_id
            new_service_item.title = f"{new_service_item.title} (Copy)"
            new_service_item.status = "draft"
            new_service_item.reviewCount = 0
            new_service_item.rating = 0

            await new_service_item.save()
            return ServiceResult(await new_service_item.to_read_model())
        except Exception as e:
            print_exc()
            return ServiceResult(AppException.CreateItem())
