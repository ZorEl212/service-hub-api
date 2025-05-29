import uuid
from traceback import print_exc
from typing import List, Optional

from beanie import PydanticObjectId
from fastapi import UploadFile

import models
from models.customer import Customer
from models.review import Review
from models.service import ServiceItem
from models.user import User
from schemas.review import ReviewCreate, ReviewUpdate
from services.app import AppCRUD
from utils.exceptions import AppException
from utils.service_result import ServiceResult


class ReviewCRUD(AppCRUD):
    async def create_review(
        self, data: ReviewCreate, files: Optional[List[UploadFile]], user: User
    ) -> ServiceResult:
        customer = await models.storage.get_by_reference(Customer, "user_id", PydanticObjectId(user.id))
        service = await models.storage.get(ServiceItem, PydanticObjectId(data.service_id))
        if not customer:
            return ServiceResult(AppException.ItemRequiresAuth())
        try:
            existing_review = await Review.find_one(
                Review.service_id.id == service.id,
                Review.user_id.id == customer.id,
            )
            print("Existing review: ", existing_review)
            if existing_review:
                return ServiceResult(
                    AppException.CreateItem({"message": "Review already exists"})
                )

            # Process attachments if any
            attachments = {}
            #if files:
            #    for file in files:
            #        id = uuid.uuid4()
            #        public_id = f"review_{service.id}_{id}"
            #        result = self.media_storage.upload(file, public_id)
            #        attachments[id] = {
            #            "public_id": public_id,
            #            "url": result["secure_url"],
            #        }

            # Create review
            review = Review(
                service_id=service,
                user_id=customer,
                rating=data.rating,
                message=data.message,
                attachments=attachments,
            )
            await review.save()

            # Update service rating
            # Calculate new average rating
            all_reviews = await self.db.get_by_reference(Review, "service_id", service.id, batch=True)
            new_rating = sum(r.rating for r in all_reviews) / len(all_reviews) if all_reviews else 0
            service.rating = new_rating
            service.reviewCount = len(all_reviews)
            await service.save()

            return ServiceResult(await review.to_read_model())
        except Exception as e:
            print_exc()
            return ServiceResult(AppException.CreateItem(
                {"message": "Failed to create review", "error": str(e)}
            ))

    async def get_service_reviews(
        self, service_id: str, page: int = 1, limit: int = 10
    ) -> ServiceResult:
        try:
            skip = (page - 1) * limit
            reviews = (
                await Review.find(Review.service_id.id == PydanticObjectId(service_id))
                .sort(-Review.created_at)
                .skip(skip)
                .limit(limit)
                .to_list()
            )

            total = await Review.find(
                Review.service_id.id == PydanticObjectId(service_id)
            ).count()

            result = {
                "page": page,
                "limit": limit,
                "total": total,
                "reviews": [await review.to_read_model() for review in reviews],
            }
            return ServiceResult(result)
        except Exception as e:
            print_exc()
            return ServiceResult(AppException.GetItem())

    async def update_review(
        self,
        review_id: str,
        data: ReviewUpdate,
        files: Optional[List[UploadFile]],
        user: User,
    ) -> ServiceResult:
        try:
            review = await self.db.get(Review, PydanticObjectId(review_id), True)
            customer = await self.db.get_by_reference(Customer, "user_id", PydanticObjectId(user.id))
            if not review:
                return ServiceResult(AppException.NotFound({"message": "Review not found"}))

            if review.user_id.id != customer.id:
                return ServiceResult(AppException.Unauthorized({"message": "Unauthorized to update this review"}))

            # Update fields
            if data.rating is not None:
                review.rating = data.rating
            if data.message is not None:
                review.message = data.message

            # Process new attachments if any
            if files:
                for file in files:
                    id = uuid.uuid4()
                    public_id = f"review_{id}"
                    result = self.media_storage.upload(file, public_id)
                    review.attachments[id] = {
                        "public_id": public_id,
                        "url": result["secure_url"],
                    }

            await review.save()

            # Update service rating
            service = await self.db.get(ServiceItem, PydanticObjectId(review_id))
            if service:
                all_reviews = await Review.find(
                    Review.service_id.id == service.id
                ).to_list()
                new_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
                service.rating = new_rating
                await service.save()

            return ServiceResult(await review.to_read_model())
        except Exception as e:
            print_exc()
            return ServiceResult(AppException.UpdateItem({"message": "Failed to update review", "error": str(e)}))

    async def delete_review(self, review_id: str, user: User) -> ServiceResult:
        try:
            review = await self.db.get(Review, PydanticObjectId(review_id), True)
            customer = await self.db.get_by_reference(Customer, "user_id", PydanticObjectId(user.id))
            if not review:
                return ServiceResult(AppException.NotFound({"message": "Review not found"}))

            if review.user_id.id != customer.id:
                return ServiceResult(AppException.Unauthorized({"message": "Unauthorized to delete this review"}))

            service = review.service_id
            await review.delete()

            # Update service rating
            if service:
                all_reviews = await Review.find(
                    Review.service_id.id == service.id
                ).to_list()
                if all_reviews:
                    new_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
                    service.rating = new_rating
                else:
                    service.rating = 0
                service.reviewCount = len(all_reviews)
                await service.save()

            return ServiceResult(True)
        except Exception as e:
            print_exc()
            return ServiceResult(AppException.DeleteItem({"message": "Failed to delete review", "error": str(e)}))

    async def mark_helpful(self, review_id: str, user: User) -> ServiceResult:
        try:
            review = await self.db.get(Review, PydanticObjectId(review_id), True)
            if not review:
                return ServiceResult(AppException.NotFound({"message": "Review not found"}))

            # Check if user already marked as helpful
            if user.id in [u.id for u in review.helpful_users]:
                # Remove helpful mark
                review.helpful_users = [
                    u for u in review.helpful_users if u.id != user.id
                ]
                review.helpful_count -= 1
            else:
                # Add helpful mark
                review.helpful_users.append(user)
                review.helpful_count += 1

            await review.save()
            return ServiceResult(await review.to_read_model())
        except Exception as e:
            print_exc()
            return ServiceResult(AppException.UpdateItem({"message": "Failed to mark review as helpful", "error": str(e)}))
