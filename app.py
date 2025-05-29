import dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

import models
from models import auth
from routers import provider, public, review, service, socket, customer
from utils.exceptions import AppExceptionCase, app_exception_handler
from utils.request_exceptions import (
    http_exception_handler,
    request_validation_exception_handler,
)

origins = [
    "http://localhost",
    "http://localhost:3000",
]

dotenv.load_dotenv(".env")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, e):
    return await http_exception_handler(request, e)


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request, e):
    return await request_validation_exception_handler(request, e)


@app.exception_handler(AppExceptionCase)
async def custom_app_exception_handler(request, e):
    return await app_exception_handler(request, e)


# Auth routes
app.include_router(auth.get_bearer_auth_router(), prefix="/auth", tags=["auth"])
app.include_router(auth.get_cookie_auth_router(), prefix="/auth/cookie", tags=["auth"])
app.include_router(auth.get_register_router(), prefix="/auth", tags=["auth"])
app.include_router(auth.get_users_router(), prefix="/users", tags=["users"])
app.include_router(auth.get_verify_router(), prefix="/email", tags=["verify"])
app.include_router(
    auth.get_reset_password_router(), prefix="/reset-password", tags=["reset-password"]
)
app.include_router(socket.router, prefix="/api/socket", tags=["Socket"])


app.include_router(public.router)
app.include_router(service.router)

app.include_router(customer.router)

app.include_router(provider.router)

app.include_router(review.router)


@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    if hasattr(models.storage, "reload"):
        print("Reloading DB")
        await models.storage.reload()


@app.get("/")
async def root():
    return {"message": "Hello World"}
