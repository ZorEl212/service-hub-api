from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_users import schemas

from models import auth, storage
from models.service import Service
from models.user import User
from schemas.service import CategoryCreate, CategoryRead
from schemas.service_provider import ServiceProvider, ServiceProviderUpdate
from models.service_provider import ServiceProvider as ServiceProviderModel
from services.service import CategoryCRUD

router = APIRouter(
    prefix="/provider",
    tags=["Providers"],
    responses={404: {"description": "Not found"}},
)

@router.get("/me", response_model=ServiceProvider)
async def get_me(user: ServiceProviderModel = Depends(auth.current_user)):
    """
    Get the current user.
    """
    details = await storage.get_by_reference(ServiceProviderModel, "user_id", user.id)
    if details:
        details.user_id = user.id
        return details
    return None

@router.put("/profile", response_model=ServiceProvider)
async def update_profile(provider_data: ServiceProviderUpdate,
    user: ServiceProviderModel = Depends(auth.current_user)

):
    """
    Update the current user's profile.
    """
    details: ServiceProviderModel = await storage.get_by_reference(ServiceProviderModel, "user_id", user.id)
    if details:
        await details.set(provider_data.model_dump())
        details.user_id = user.id
        return details
    return None
