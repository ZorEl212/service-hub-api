from traceback import print_exception

from models.user import User
from models.customer import Customer
from models.service_provider import ServiceProvider
from schemas.user import UserCreate
from services.app import AppCRUD
from utils.exceptions import AppException
from utils.service_result import ServiceResult


class UserCRUD(AppCRUD):
    """
    User CRUD operations including profile creation based on role.
    """

    @staticmethod
    async def create_profile_for_user(
        user: User,
        user_data: UserCreate,
    ) -> ServiceResult:
        """
        Attach a role-specific profile (customer or provider) to an existing user.
        Assumes user is already created by fastapi-users.
        :param user: User instance (already saved)
        :param user_data: UserCreateExtended with optional profile data
        :return: ServiceResult
        """
        try:
            if user_data.role == "customer":
                if not user_data.customer_profile:
                    return ServiceResult(AppException.BadRequest())

                customer_profile = Customer(
                    user_id=user
                    **user_data.customer_profile.model_dump(mode="python")
                )
                await customer_profile.insert()

            elif user_data.role == "provider":
                if not user_data.provider_profile:
                    return ServiceResult(AppException.BadRequest())

                provider_profile = ServiceProvider(
                    user_id=user,
                    **user_data.provider_profile.model_dump(mode="python")
                )
                await provider_profile.insert()

            return ServiceResult(user)

        except Exception as e:
            print_exception(*e.args)
            return ServiceResult(AppException.CreateItem())
