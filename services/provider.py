import uuid

from beanie import PydanticObjectId
from fastapi import UploadFile

from models import media_storage, sms_auth, storage
from models.service_provider import ServiceProvider
from models.user import User
from schemas.service_provider import PublicServiceProviderRead, ServiceProviderCreate
from services.app import AppCRUD
from utils.exceptions import AppException
from utils.service_result import ServiceResult

class ServiceProviderCRUD(AppCRUD):
    """
    Handles Create, Read, Update, and Delete (CRUD) operations for service providers.

    This class is responsible for defining methods and utilities to manage service
    provider entities in the application. It builds upon the generic `AppCRUD`
    parent class and may include additional functionality specific to service
    providers.
    """

    async def get_me(self, user: User) -> ServiceResult:
        """
        Retrieves the service provider details for the current user.

        :param user: The current user instance.
        :return: A ServiceResult containing the service provider details or an error.
        """
        if user.role != "provider":
            return ServiceResult(AppException.Forbidden({
                "message": "User is not a service provider"
            }))
        profile: ServiceProvider = await storage.get_by_reference(ServiceProvider, "user_id", user.id)
        if profile:
            return ServiceResult(await profile.to_read_model())
        return ServiceResult(AppException.NotFound({"message": "Service provider not found"}))

    async def get_public_profile(self, provider_id: str) -> ServiceResult:
        """
        Retrieves the public profile of a service provider by their ID.

        :param provider_id: The ID of the service provider.
        :return: A ServiceResult containing the service provider details or an error.
        """
        provider: ServiceProvider = await self.db.get(ServiceProvider, PydanticObjectId(provider_id), fetch_links=True)
        if not provider:
            return ServiceResult(AppException.NotFound({"message": "Service provider not found"}))
        provider_data = provider.model_dump(mode="python")
        provider_data["email"] = provider.user_id.email if provider.user_id else None
        print(provider_data)

        if not isinstance(provider_data, dict):
            return ServiceResult(AppException.GetItem({"message": "Invalid provider data"}))

        public_profile = PublicServiceProviderRead(**provider_data)
        print(public_profile)
        return ServiceResult(public_profile)

    async def update_profile_picture(self, file: UploadFile, user: User) -> ServiceResult:
        """
        Uploads a profile picture for the service provider.

        :param file: The image file to upload.
        :param user: The service provider instance.
        :return: A ServiceResult indicating success or failure.
        """
        if file.content_type not in ["image/jpeg", "image/png"]:
            return ServiceResult(AppException.CreateItem())
        provider: ServiceProvider = await storage.get_by_reference(ServiceProvider, "user_id", user.id)
        if not provider:
            return ServiceResult(AppException.CreateItem())
        if not file.filename:
            return ServiceResult(AppException.CreateItem())

        id = uuid.uuid4()
        public_id = f"{provider.id}_{id}"
        result = media_storage.upload(file, public_id=public_id)
        provider.profile_picture = result.get("secure_url", "")
        await provider.set({"profile_picture": provider.profile_picture})
        return ServiceResult(await provider.to_read_model())

    async def request_phone_verification(self, phone: str) -> ServiceResult:
        """
        Requests phone number verification for the service provider.

        :param phone: The phone number to verify.
        :return: A ServiceResult indicating success or failure.
        """
        if not phone:
            return ServiceResult(AppException.InvalidPhoneNumber())

        provider = await storage.get_by_reference(ServiceProvider, "phone", phone)
        if provider:
            return ServiceResult(AppException.PhoneAlreadyRegistered())

        result = await sms_auth.send_verification(phone)
        if result:
            return ServiceResult({"message": "Verification code sent successfully."})

        return ServiceResult(AppException.SMSVerificationRequestFailed())

    async def verify_phone_number(self, phone: str, code: str) -> ServiceResult:
        """
        Verifies the phone number with the provided code.

        :param phone: The phone number to verify.
        :param code: The verification code sent to the phone.
        :return: A ServiceResult indicating success or failure.
        """
        if not phone or not code:
            return ServiceResult(AppException.InvalidPhoneNumber())

        result = await sms_auth.check_verification(phone, code)
        if result:
            return ServiceResult({"message": "Phone number verified successfully."})

        return ServiceResult(AppException.SMSVerificationFailed())