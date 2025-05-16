import json

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from fastapi_users import exceptions, models, schemas
from fastapi_users.authentication import AuthenticationBackend, Authenticator, Strategy
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorCode, ErrorModel

from services.user import UserCRUD


class AuthRoutes:
    @classmethod
    def get_register_router(cls,
        get_user_manager: UserManagerDependency[models.UP, models.ID],
        user_schema: type[schemas.U],
        user_create_schema: type[schemas.UC],
    ) -> APIRouter:
        """Generate a router with the register route."""
        router = APIRouter()

        @router.post(
            "/register",
            response_model=user_schema,
            status_code=status.HTTP_201_CREATED,
            name="register:register",
            responses={
                status.HTTP_400_BAD_REQUEST: {
                    "model": ErrorModel,
                    "content": {
                        "application/json": {
                            "examples": {
                                ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                                    "summary": "A user with this email already exists.",
                                    "value": {
                                        "detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS
                                    },
                                },
                                ErrorCode.REGISTER_INVALID_PASSWORD: {
                                    "summary": "Password validation failed.",
                                    "value": {
                                        "detail": {
                                            "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                                            "reason": "Password should be"
                                            "at least 3 characters",
                                        }
                                    },
                                },
                            }
                        }
                    },
                },
            },
        )
        async def register(
            request: Request,
            user_create: user_create_schema,
            user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        ):
            try:
                created_user = await user_manager.create(
                    user_create, safe=True, request=request
                )
            except exceptions.UserAlreadyExists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
                )
            except exceptions.InvalidPasswordException as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                        "reason": e.reason,
                    },
                )

            result = await UserCRUD.create_profile_for_user(created_user, user_create)

            if not result.success:
                raise HTTPException(status_code=400, detail=str(result.exception_case))

            return schemas.model_validate(user_schema, created_user)

        return router

    @classmethod
    def get_auth_router(cls,
            backend: AuthenticationBackend[models.UP, models.ID],
            get_user_manager: UserManagerDependency[models.UP, models.ID],
            authenticator: Authenticator[models.UP, models.ID],
            requires_verification: bool = False,
    ) -> APIRouter:
        """Generate a router with login/logout routes for an authentication backend."""
        router = APIRouter()
        get_current_user_token = authenticator.current_user_token(
            active=True, verified=requires_verification
        )

        login_responses: OpenAPIResponseType = {
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.LOGIN_BAD_CREDENTIALS: {
                                "summary": "Bad credentials or the user is inactive.",
                                "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                            },
                            ErrorCode.LOGIN_USER_NOT_VERIFIED: {
                                "summary": "The user is not verified.",
                                "value": {"detail": ErrorCode.LOGIN_USER_NOT_VERIFIED},
                            },
                        }
                    }
                },
            },
            **backend.transport.get_openapi_login_responses_success(),
        }

        @router.post(
            "/login",
            name=f"auth:{backend.name}.login",
            responses=login_responses,
        )
        async def login(
                request: Request,
                credentials: OAuth2PasswordRequestForm = Depends(),
                user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
                strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
        ):
            user = await user_manager.authenticate(credentials)

            if user is None or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
                )
            if requires_verification and not user.is_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.LOGIN_USER_NOT_VERIFIED,
                )
            response = await backend.login(strategy, user)
            await user_manager.on_after_login(user, request, response)

            # Append user role to the response body if available
            if hasattr(user, "role"):
                body_data = json.loads(response.body)
                body_data["role"] = user.role
                response.body = json.dumps(body_data).encode("utf-8")
                response.headers["Content-Length"] = str(len(response.body))

            print(response.body)
            await user_manager.on_after_login(user, request, response)
            return response

        logout_responses: OpenAPIResponseType = {
            **{
                status.HTTP_401_UNAUTHORIZED: {
                    "description": "Missing token or inactive user."
                }
            },
            **backend.transport.get_openapi_logout_responses_success(),
        }

        @router.post(
            "/logout", name=f"auth:{backend.name}.logout", responses=logout_responses
        )
        async def logout(
                user_token: tuple[models.UP, str] = Depends(get_current_user_token),
                strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
        ):
            user, token = user_token
            return await backend.logout(strategy, user, token)

        return router

