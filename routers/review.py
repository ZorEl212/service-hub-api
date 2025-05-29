from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile

from models import auth
from models.user import User
from schemas.review import ReviewCreate, ReviewRead, ReviewUpdate
from services.review import ReviewCRUD

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=ReviewRead)
async def create_review(
    service_id: str = Form(...),
    rating: float = Form(...),
    message: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    user: User = Depends(auth.current_user),
):
    data = ReviewCreate(service_id=service_id, rating=rating, message=message)
    result = await ReviewCRUD().create_review(data=data, files=files, user=user)
    if result.success:
        print("Success")
        return result.value
    print("Failed")
    raise result.exception_case


@router.get("/service/{service_id}", response_model=dict)
async def get_service_reviews(
    service_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    user: User = Depends(auth.optional_current_user),
):
    result = await ReviewCRUD().get_service_reviews(
        service_id=service_id, page=page, limit=limit
    )
    if result.success:
        return result.value
    return result.exception_case


@router.put("/{review_id}", response_model=ReviewRead)
async def update_review(
    review_id: str,
    rating: Optional[float] = Form(None),
    message: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    user: User = Depends(auth.current_user),
):
    data = ReviewUpdate(rating=rating, message=message)
    result = await ReviewCRUD().update_review(
        review_id=review_id, data=data, files=files, user=user
    )
    if result.success:
        return result.value
    return result.exception_case


@router.delete("/{review_id}")
async def delete_review(review_id: str, user: User = Depends(auth.current_user)):
    result = await ReviewCRUD().delete_review(review_id=review_id, user=user)
    if result.success:
        return {"message": "Review deleted successfully"}
    return result.exception_case


@router.post("/{review_id}/helpful", response_model=ReviewRead)
async def mark_review_helpful(review_id: str, user: User = Depends(auth.current_user)):
    result = await ReviewCRUD().mark_helpful(review_id=review_id, user=user)
    if result.success:
        return result.value
    return result.exception_case
