"""
API v1 router - Main API router for version 1.
"""

from fastapi import APIRouter
from .endpoints import health, srs, wireframes, diagrams, conversations

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(srs.router, prefix="/srs", tags=["srs"])
api_router.include_router(wireframes.router, prefix="/wireframes", tags=["wireframes"])
api_router.include_router(diagrams.router, prefix="/diagrams", tags=["diagrams"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])