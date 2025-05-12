from fastapi import APIRouter, Depends

from models import auth, storage
from models.engine.file_storage import FileStorage
from schemas.service_provider import ServiceProviderCreate, ServiceProvider
from models.service_provider import ServiceProvider as ServiceProviderModel
from services.user import UserCRUD


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
    print(user.dict())
    details = await storage.get_by_reference(ServiceProviderModel, "user_id", user.id)
    print(details)
    if details:
        details.user_id = user.id
        return details
    return None
