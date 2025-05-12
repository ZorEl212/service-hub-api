from typing import Optional
from urllib.request import Request

from beanie import PydanticObjectId
from fastapi import Depends
from fastapi_users.authentication import BearerTransport, JWTStrategy, AuthenticationBackend
from fastapi_users_db_beanie import BeanieUserDatabase, ObjectIDIDMixin

from models import storage
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


class Auth:
    def __init__(self):
        self.secret = SECRET
        self.transport = BearerTransport(tokenUrl="auth/jwt/login")
        self.backend = AuthenticationBackend(
            name="jwt",
            transport=self.transport,
            get_strategy=self.get_jwt_strategy,
        )

        self.fastapi_users = FastAPIUsers[User, PydanticObjectId](
            self.get_user_manager,
            [self.backend],
        )
        self.auth_routes = AuthRoutes()

        self.current_user = self.fastapi_users.current_user()
        self.current_active_user = self.fastapi_users.current_user(active=True)
        self.current_superuser = self.fastapi_users.current_user(superuser=True)

    def get_jwt_strategy(self) -> JWTStrategy:
        return JWTStrategy(secret=self.secret, lifetime_seconds=3600)

    def get_auth_router(self):
        return self.fastapi_users.get_auth_router(self.backend)

    def get_register_router(self):
        return self.auth_routes.get_register_router(self.fastapi_users.get_user_manager, UserRead, UserCreate)

    def get_verify_router(self):
        return self.fastapi_users.get_verify_router(UserRead)

    def get_users_router(self):
        return self.fastapi_users.get_users_router(UserRead, UserUpdate)

    async def get_user_manager(self, user_db: BeanieUserDatabase = Depends(storage.get_user_db)):
        yield UserManager(user_db)
