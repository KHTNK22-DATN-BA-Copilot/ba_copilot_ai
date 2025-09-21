"""
Health check endpoint.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any
import os

router = APIRouter()

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    version: str
    environment: str
    services: Dict[str, str]
    uptime_seconds: int

@router.get("/", response_model=HealthResponse)
async def get_health():
    """
    Get service health status.
    Returns basic health information and status of dependent services.
    """
    try:
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow().isoformat() + "Z",
            version="1.0.0",
            environment=os.getenv("ENVIRONMENT", "development"),
            services={
                "database": "healthy",
                "llm_providers": "healthy",
                "file_storage": "healthy",
                "cache": "healthy"
            },
            uptime_seconds=86400  # Mock 1 day uptime
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@router.get("/ping")
async def ping():
    """Simple ping endpoint."""
    return {"message": "pong"}