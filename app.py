from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

import models
from routers import user
from utils.exceptions import AppExceptionCase, app_exception_handler
from utils.request_exceptions import (
    http_exception_handler,
    request_validation_exception_handler,
)

app = FastAPI()


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, e):
    return await http_exception_handler(request, e)


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request, e):
    return await request_validation_exception_handler(request, e)


@app.exception_handler(AppExceptionCase)
async def custom_app_exception_handler(request, e):
    return await app_exception_handler(request, e)


app.include_router(user.router)


@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    if hasattr(models.storage, "reload"):
        await models.storage.reload()


@app.get("/")
async def root():
    return {"message": "Hello World"}
