from fastapi import APIRouter, Depends

from models.engine.file_storage import FileStorage
from schemas.user import User, UserCreate
from services.user import UserCRUD
from utils.service_result import handle_result

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=User)
async def create_item(item: UserCreate):
    result = await UserCRUD().create_user(item)
    return handle_result(result)


@router.get("/item/{item_id}", response_model=User)
async def get_item(item_id: str):
    result = await UserCRUD().get_user(user_id=item_id)
    return handle_result(result)
