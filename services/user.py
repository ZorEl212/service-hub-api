from models.user import User
from schemas.user import UserCreate
from services.app import AppCRUD
from utils.exceptions import AppException
from utils.service_result import ServiceResult


class UserCRUD(AppCRUD):
    """
    User CRUD operations.
    """

    async def create_user(self, user: UserCreate) -> User | ServiceResult:
        """
        Create a new user.
        :param user: UserCreate
        :return: User
        """
        new_user = User.from_create(user)
        if not new_user:
            return ServiceResult(AppException.CreateItem())
        print(f"Storage instance: {type(self.db)}")
        await new_user.save()
        return ServiceResult(new_user)

    async def get_user(self, user_id: str) -> User | ServiceResult:
        """
        Get a user by ID.
        :param user_id: int
        :return: User
        """
        user = await self.db.get(cls="User", obj_id=user_id)
        if not user:
            return ServiceResult(AppException.GetItem())
        return ServiceResult(user)
