from services.app import AppCRUD
from utils.exceptions import AppException
from utils.service_result import ServiceResult

from models.customer import Customer
from models.user import User

class CustomerCRUD(AppCRUD):
    """
    Handles Create, Read, Update, and Delete (CRUD) operations for customers.

    This class is responsible for defining methods and utilities to manage customer
    entities in the application. It builds upon the generic `AppCRUD` parent class
    and may include additional functionality specific to customers.
    """

    async def get_me(self, user: User) -> ServiceResult:
        """
        Retrieves the customer details for the current user.

        :param user: The current user instance.
        :return: A ServiceResult containing the customer details or an error.
        """
        if user.role != "customer":
            return ServiceResult(AppException.Forbidden({
                "message": "User is not a customer"
            }))

        profile: Customer = await self.db.get_by_reference(Customer, "user_id", user.id)
        if profile:
            return ServiceResult(await profile.to_read_model())
        return ServiceResult(AppException.NotFound({
            "message": "Customer not found"
        }))
