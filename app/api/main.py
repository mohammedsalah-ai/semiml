"""
Consolidatie all routers in one
"""

from fastapi import APIRouter
from app.api.routers import auth, users, files, experiments

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(
    experiments.router, prefix="/experiments", tags=["experiments"]
)
