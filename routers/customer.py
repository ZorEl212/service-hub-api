from fastapi import APIRouter, Depends

from models import auth
from models.user import User
from schemas.customer import CustomerRead
from services.customer import CustomerCRUD

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    responses={404: {"description": "Not found"}},
)
@router.get("/me", response_model=CustomerRead)
async def get_me(user: User = Depends(auth.current_user)):
    """
    Get the current user.
    """
    result = await CustomerCRUD().get_me(user)
    if result.success:
        return result.value

    raise result.exception_case