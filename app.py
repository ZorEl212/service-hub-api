from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware

import models
from models import auth
from routers import user
from routers import provider
from utils.exceptions import AppExceptionCase, app_exception_handler
from utils.request_exceptions import (
    http_exception_handler,
    request_validation_exception_handler,
)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:3000",
]

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
app.include_router(auth.get_auth_router(), prefix="/auth/jwt", tags=["auth"])
app.include_router(auth.get_register_router(), prefix="/auth", tags=["auth"])
app.include_router(auth.get_users_router(), prefix="/users", tags=["users"])

app.include_router(user.router)

app.include_router(provider.router)


@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    if hasattr(models.storage, "reload"):
        await models.storage.reload()


@app.get("/")
async def root():
    return {"message": "Hello World"}
