from fastapi import Request
from starlette.responses import JSONResponse


class AppExceptionCase(Exception):
    def __init__(self, status_code: int, context: dict = None):
        self.exception_case = self.__class__.__name__
        self.status_code = status_code
        self.context = context or {}

    def __str__(self):
        return (
            f"<AppException {self.exception_case} - "
            f"status_code={self.status_code} - context={self.context}>"
        )


async def app_exception_handler(request: Request, exc: AppExceptionCase):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "app_exception": exc.exception_case,
            "context": exc.context,
        },
    )


class AppException(Exception):
    """Base exception class for application-specific exceptions"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class AppException:
    class CreateItem(AppExceptionCase):
        def __init__(self, context: dict = None):
            super().__init__(status_code=500, context=context)

    class GetItem(AppExceptionCase):
        def __init__(self, context: dict = None):
            super().__init__(status_code=404, context=context)

    class BadRequest(AppExceptionCase):
        def __init__(self, context: dict = None):
            super().__init__(status_code=400, context=context)

    class ItemRequiresAuth(AppExceptionCase):
        def __init__(self, context: dict = None):
            super().__init__(status_code=401, context=context)

    class Unauthorized(AppExceptionCase):
        def __init__(self, context: dict = None):
            super().__init__(status_code=401, context=context)

    class Forbidden(AppExceptionCase):
        def __init__(self, context: dict = None):
            super().__init__(status_code=403, context=context)

    class NotFound(AppExceptionCase):
        def __init__(self, context: dict = None):
            super().__init__(status_code=404, context=context)

    class UpdateItem(AppExceptionCase):
        def __init__(self, context: dict = None):
            super().__init__(status_code=500, context=context)

    class DeleteItem(AppExceptionCase):
        def __init__(self, context: dict = None):
            super().__init__(status_code=500, context=context)

    class InvalidPhoneNumber(AppExceptionCase):
        def __init__(self, context: dict = None):
            super().__init__(status_code=400, context=context)

    class SMSVerificationRequestFailed(AppExceptionCase):
        def __init__(self, context: dict = None):
            super().__init__(status_code=500, context=context)

    class SMSVerificationFailed(AppExceptionCase):
        def __init__(self, context: dict = None):
            super().__init__(status_code=401, context=context)

    class PhoneAlreadyRegistered(AppExceptionCase):
        def __init__(self, context: dict = None):
            super().__init__(status_code=409, context=context)
