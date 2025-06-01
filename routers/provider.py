from typing import List

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile

from models import auth, storage
from models.user import User
from schemas.service import CategoryCreate, CategoryRead, CategorySync, PublicCategoryRead
from schemas.service_provider import PublicServiceProviderRead, ServiceProvider, ServiceProviderUpdate
from models.service_provider import ServiceProvider as ServiceProviderModel
from services.provider import ServiceProviderCRUD
from services.service import CategoryCRUD

router = APIRouter(
    prefix="/provider",
    tags=["Providers"],
    responses={404: {"description": "Not found"}},
)

@router.get("/me", response_model=ServiceProvider)
async def get_me(user: User = Depends(auth.current_user)):
    """
    Get the current user.
    """
    result = await ServiceProviderCRUD().get_me(user)
    if result.success:
        return result.value
    raise result.exception_case

@router.put("/profile", response_model=ServiceProvider)
async def update_profile(provider_data: ServiceProviderUpdate,
    user: User = Depends(auth.current_user)

):
    """
    Update the current user's profile.
    """
    result = await ServiceProviderCRUD().update_profile(provider_data, user)
    if result.success:
        return result.value
    raise result.exception_case

@router.post("/profile/picture", response_model=ServiceProvider)
async def upload_profile_picture(
    file: UploadFile = File(...),
    user: User = Depends(auth.current_user)
):
    """
    Upload a profile picture for the current user.
    """

    result = await ServiceProviderCRUD().update_profile_picture(file, user)
    if result.success:
        return result.value
    return result.exception_case

@router.post("/categories", response_model=CategorySync)
async def sync_category(categories: List[CategoryCreate], user: User = Depends(auth.current_user)):
    """
    Create a new category.
    """
    result = await CategoryCRUD().sync_categories(categories, user)
    if result.success:
        return result.value
    raise HTTPException(status_code=400, detail=result.exception_case)

@router.get("/categories", response_model=list[CategoryRead])
async def get_categories(user: User = Depends(auth.current_user)):
    """
    Get all categories.
    """
    result = await CategoryCRUD().get_all(user)
    if result.success:
        return [await item.to_read_model() for item in result.value]
    raise HTTPException(status_code=400, detail=result.exception_case)

@router.get("/categories/{provider_id}", response_model=list[PublicCategoryRead])
async def get_by_provider(provider_id: str):
    """
    Get categories by provider ID.
    """
    result = await CategoryCRUD().get_by_provider(provider_id)
    if result.success:
        return result.value
    raise result.exception_case

@router.get("/request_sms")
async def request_sms_verification(
    phone: str
):
    """
    Request SMS verification for the current user.
    """
    result = await ServiceProviderCRUD().request_phone_verification(phone)
    if result.success:
        return result.value
    raise HTTPException(status_code=400, detail=result.exception_case)

@router.get("/verify_sms")
async def verify_sms_code(
    phone: str,
    code: str
):
    """
    Verify the SMS code for the current user.
    """
    result = await ServiceProviderCRUD().verify_phone_number(phone, code)
    if result.success:
        return result.value
    raise HTTPException(status_code=400, detail=result.exception_case)

@router.get("/public/{provider_id}", response_model=PublicServiceProviderRead)
async def get_public_profile(provider_id: str):
    """
    Get public profile of a service provider.
    """
    result = await ServiceProviderCRUD().get_public_profile(provider_id)
    if result.success:
        return result.value
    raise result.exception_case
