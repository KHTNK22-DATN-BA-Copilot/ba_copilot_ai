"""
FastAPI application entry point for BA Copilot AI Services.
"""

import logging
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from api.v1.router import api_router
from core.config import settings


def setup_logging():
    """Configure application logging."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(log_level)
    logging.getLogger("fastapi").setLevel(log_level)


def create_app() -> FastAPI:
    """Create FastAPI application with middleware and routes."""
    # Setup logging first
    setup_logging()
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode")
    
    app = FastAPI(
        title=settings.app_name,
        description="AI-powered services for Business Analysts",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        debug=settings.debug,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router, prefix="/v1")
    
    logger.info(f"Application configured with CORS origins: {settings.allowed_origins}")
    
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )