from fastapi import FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
