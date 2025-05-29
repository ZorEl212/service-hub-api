import argparse
import asyncio
import os

import dotenv
import uvicorn


def check_env():
    if not dotenv.find_dotenv():
        raise FileNotFoundError("No .env file found")
    dotenv.load_dotenv(".env")

async def main():
    check_env()
    uvicorn.run("app:app", port=5000, log_level="info", reload=True)


if __name__ == "__main__":
    asyncio.run(main())
