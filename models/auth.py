from traceback import print_exc
from typing import Optional
from urllib.request import Request

from beanie import PydanticObjectId
from fastapi import Depends
from fastapi_users.authentication import BearerTransport, CookieTransport, JWTStrategy, AuthenticationBackend
from fastapi_users_db_beanie import BeanieUserDatabase, ObjectIDIDMixin
from starlette.websockets import WebSocket

from models import email_client, storage
from routers.auth import AuthRoutes
from schemas.user import UserCreate, User as UserRead, UserUpdate
from models.user import User

from fastapi_users import BaseUserManager, FastAPIUsers

SECRET = "SUPERSECRETJWTKEY"


class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")
        await email_client.send_verification_email(user.email, token)


class Auth:
    def __init__(self):
        self.secret = SECRET
        self.bearer_transport = BearerTransport(tokenUrl="auth/login")

        self.cookie_transport = CookieTransport(
            cookie_name="auth_token",
            cookie_max_age=3600,  # in seconds
            cookie_samesite="lax",  # Adjust as needed
        )
        self.bearer_backend = AuthenticationBackend(
            name="jwt",
            transport=self.bearer_transport,
            get_strategy=self.get_jwt_strategy,
        )

        self.cookie_backend = AuthenticationBackend(
            name="cookie",
            transport=self.cookie_transport,
            get_strategy=self.get_jwt_strategy
        )
        self.fastapi_users = FastAPIUsers[User, PydanticObjectId](
            self.get_user_manager,
            [self.bearer_backend, self.cookie_backend],
        )
        self.auth_routes = AuthRoutes()

        self.current_user = self.fastapi_users.current_user()
        self.optional_current_user = self.fastapi_users.current_user(optional=True)
        self.current_active_user = self.fastapi_users.current_user(active=True)
        self.current_superuser = self.fastapi_users.current_user(superuser=True)

    async def get_user_from_cookie(self, websocket: WebSocket, user_manager: BaseUserManager):
        cookie_value = websocket.cookies.get(self.cookie_transport.cookie_name)
        if not cookie_value:
            return None
        try:
            # Validate and get user using FastAPI Users token logic
            user = await self.cookie_backend.get_strategy().read_token(cookie_value, user_manager)
            return await user_manager.get(user.id)
        except Exception as e:
            print_exc()
            return None

    def get_jwt_strategy(self) -> JWTStrategy:
        return JWTStrategy(secret=self.secret, lifetime_seconds=3600)

    def get_bearer_auth_router(self):
        return self.auth_routes.get_auth_router(self.bearer_backend, self.fastapi_users.get_user_manager, self.fastapi_users.authenticator, False)

    def get_cookie_auth_router(self):
        return self.auth_routes.get_auth_router(self.cookie_backend, self.fastapi_users.get_user_manager, self.fastapi_users.authenticator, False)

    def get_register_router(self):
        return self.auth_routes.get_register_router(self.fastapi_users.get_user_manager, UserRead, UserCreate)

    def get_verify_router(self):
        return self.fastapi_users.get_verify_router(UserRead)

    def get_users_router(self):
        return self.fastapi_users.get_users_router(UserRead, UserUpdate)
    def get_reset_password_router(self):
        return self.fastapi_users.get_reset_password_router()

    async def get_user_manager(self, user_db: BeanieUserDatabase = Depends(storage.get_user_db)):
        yield UserManager(user_db)
