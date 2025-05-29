from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from models import auth, sms_auth
from services.search import SearchEngine
from models.user import User
from schemas.generic_schemas import SearchFilters
from services.service import CategoryCRUD, ServiceItemCRUD

router = APIRouter(
    tags=["Public"],
    responses={404: {"description": "Not found"}},
)
@router.post("/search", response_model=dict)
async def search_services(search_data: SearchFilters,
        user: User = Depends(auth.optional_current_user)
):
    engine = SearchEngine()
    result = await engine.search(search_data)
    if result.success:
        return result.value
    return result.exception_case

