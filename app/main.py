"""
ASGI FastAPI application

exposes the main ASGI application, that includes the main router
"""

from fastapi import FastAPI
from app.api.main import api_router


app = FastAPI()


app.include_router(api_router)
