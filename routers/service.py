import json
from typing import Annotated, List, Optional

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, File, UploadFile, Form, Query

from models import auth
from models.user import User
from schemas.service import PublicServiceItemRead, ServiceItemCreate, ServiceItemRead, ServiceItemUpdate
from services.service import ServiceItemCRUD

router = APIRouter(
    prefix="/provider/services",
    tags=["Services"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=ServiceItemRead)
async def create_service(
        title: Annotated[str, Form()],
        description: Annotated[str, Form()],
        price: Annotated[float, Form()],
        featured: Annotated[bool, Form()],
        image_urls: Annotated[str, Form()],
        category_id: Annotated[str, Form()],
        status: Annotated[str, Form()],
        images: Annotated[List[UploadFile], File(...)],
        user: User = Depends(auth.current_user)
):
    data = ServiceItemCreate(
        title=title,
        description=description,
        featured=featured,
        status=status,
        price=price,
        category_id=PydanticObjectId(category_id),
        image_urls=image_urls,
    )
    result = await ServiceItemCRUD().create_service(data=data, files=images, user=user)
    if result.success:
        return result.value
    return result.exception_case


@router.get("/", response_model=List[ServiceItemRead])
async def get_services(user: User = Depends(auth.current_user)):
    """
    Get all service items for a service provider.
    """
    result = await ServiceItemCRUD().get_all(user)
    if result.success:
        return result.value
    return result.exception_case

@router.get("/{service_id}", response_model=ServiceItemRead)
async def get_service(service_id: str, user: User = Depends(auth.current_user)):
    """
    Get a specific service item by ID.
    """
    result = await ServiceItemCRUD().get_by_id(service_id, user)
    if result.success:
        return result.value
    return result.exception_case


@router.put("/{service_id}", response_model=ServiceItemRead)
async def update_service(service_id: str, title: Annotated[str, Form()],
                         description: Annotated[str, Form()],
                         price: Annotated[float, Form()],
                         featured: Annotated[bool, Form()],
                         image_urls: Annotated[str, Form()],
                         category_id: Annotated[str, Form()],
                         status: Annotated[str, Form()],
                         images: Annotated[List[UploadFile] | None, File()] = None,
                         user: User = Depends(auth.current_user)):
    print(image_urls)
    parsed_urls = json.loads(image_urls)
    data = ServiceItemUpdate(
        title=title,
        description=description,
        featured=featured,
        status=status,
        price=price,
        category_id=PydanticObjectId(category_id),
        image_urls=parsed_urls,
    )

    result = await ServiceItemCRUD().update_service(data=data, files=images, user=user, service_item_id=service_id)
    if result.success:
        return result.value
    return result.exception_case

@router.post("/hit_counter/{service_id}")
async def service_hit_counter(service_id: str):
    """
    Increment the hit counter for a service item.
    """
    result = await ServiceItemCRUD().increment_hit_counter(service_id)
    if result.success:
        return result.value
    return result.exception_case

@router.get("/public/{provider_id}", response_model=List[PublicServiceItemRead])
async def get_public_services(provider_id: str):
    """
    Get public service items for a service provider.
    """
    result = await ServiceItemCRUD().get_all_public(provider_id)
    if result.success:
        return result.value
    raise result.exception_case

@router.delete("/{service_id}")
async def delete_service(service_id: str, user: User = Depends(auth.current_user)):
    """
    Delete a service item by ID.
    """
    result = await ServiceItemCRUD().delete_service(service_id, user)
    if result.success:
        return {"message": "Service item deleted successfully"}
    return result.exception_case


@router.get("/{service_id}/duplicate", response_model=ServiceItemRead)
async def duplicate_service(service_id: str, user: User = Depends(auth.current_user)):
    """
    Duplicate a service item by ID.
    """
    result = await ServiceItemCRUD().duplicate_service(service_id, user)
    if result.success:
        return result.value
    return result.exception_case
