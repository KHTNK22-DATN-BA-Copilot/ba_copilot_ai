# FastAPI framework and HTTP error handling
from fastapi import FastAPI, HTTPException

# CORS middleware for cross-origin requests
from fastapi.middleware.cors import CORSMiddleware

# Pydantic for request/response data validation
from pydantic import BaseModel

# Import workflow graphs for AI-powered generation
from workflows import srs_graph, class_diagram_graph, usecase_diagram_graph, activity_diagram_graph, wireframe_graph

# OS/environment variable management
import os
from dotenv import load_dotenv

# Logging setup
import logging

# subprocess imports
import asyncio
from contextlib import asynccontextmanager
from services.mermaid_validator.subprocess_manager import MermaidSubprocessManager

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Startup:
        - Create validator client
        - Wait for validator to be ready

    Shutdown:
        - Close validator client
    """
    # Startup
    logger.info("Initializing Mermaid validator client...")
    validator = MermaidSubprocessManager()

    # Wait for validator to be ready (retries if fail)
    max_retries = 30
    for i in range(max_retries):
        if await validator.health_check():
            logger.info("✅ Mermaid validator is ready")
            break
        logger.info(f"⏳ Waiting for validator to be ready... ({i+1}/{max_retries})")
        await asyncio.sleep(1 + i)
    else:
        logger.warning("⚠️ Validator not ready, proceeding without validation")

    # Store in app state
    app.state.validator = validator

    yield

    # Shutdown
    logger.info("Closing validator client...")
    await validator.close()

app = FastAPI(
    title="AI Service - BA Copilot",
    description="AI service for generating SRS, Wireframes, and Diagrams",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AIRequest(BaseModel):
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Create SRS for hotel management system"
            }
        }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "BA Copilot AI Service",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    openrouter_api_key = os.getenv("OPEN_ROUTER_API_KEY", "")
    return {
        "status": "healthy",
        "openrouter_api_configured": bool(openrouter_api_key)
    }

@app.post("/api/v1/srs/generate")
async def generate_srs(req: AIRequest):
    """
    Generate Software Requirements Specification (SRS) document.

    Args:
        req (AIRequest): Request body containing user message

    Returns:
        dict: Response with SRS data

    Example response:
        {
            "type": "srs",
            "response": {
                "title": "...",
                "functional_requirements": "...",
                "non_functional_requirements": "...",
                "detail": "..."
            }
        }
    """
    try:
        # Invoke SRS workflow
        result = srs_graph.invoke({"user_message": req.message})
        return {"type": "srs", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating SRS: {str(e)}"
        )

@app.post("/api/v1/generate/class-diagram")
async def generate_class_diagram(req: AIRequest):
    """
    Generate UML Class Diagram in Mermaid markdown format.

    Args:
        req (AIRequest): Request body containing user message

    Returns:
        dict: Response with class diagram data

    Example response:
        {
            "type": "diagram",
            "response": {
                "type": "class_diagram",
                "detail": "```mermaid\\nclassDiagram\\n...```"
            }
        }
    """
    try:
        # Invoke Class Diagram workflow
        result = class_diagram_graph.invoke({"user_message": req.message})
        return {"type": "diagram", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating class diagram: {str(e)}"
        )

@app.post("/api/v1/generate/usecase-diagram")
async def generate_usecase_diagram(req: AIRequest):
    """
    Generate UML Use Case Diagram in Mermaid markdown format.

    Args:
        req (AIRequest): Request body containing user message

    Returns:
        dict: Response with use case diagram data

    Example response:
        {
            "type": "diagram",
            "response": {
                "type": "usecase_diagram",
                "detail": "```mermaid\\ngraph TD\\n...```"
            }
        }
    """
    try:
        # Invoke Use Case Diagram workflow
        result = usecase_diagram_graph.invoke({"user_message": req.message})
        return {"type": "diagram", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating use case diagram: {str(e)}"
        )

@app.post("/api/v1/generate/activity-diagram")
async def generate_activity_diagram(req: AIRequest):
    """
    Generate UML Activity Diagram in Mermaid markdown format.

    Args:
        req (AIRequest): Request body containing user message

    Returns:
        dict: Response with activity diagram data

    Example response:
        {
            "type": "diagram",
            "response": {
                "type": "activity_diagram",
                "detail": "```mermaid\\ngraph TD\\n...```"
            }
        }
    """
    try:
        # Invoke Activity Diagram workflow
        result = activity_diagram_graph.invoke({"user_message": req.message})
        return {"type": "diagram", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating activity diagram: {str(e)}"
        )


@app.post("/api/v1/wireframe/generate")
async def generate_wireframe(req: AIRequest):
    """
    Generate wireframe/UI mockup.

    Args:
        req (AIRequest): Request body containing user message

    Returns:
        dict: Response with wireframe data

    Example response:
        {
            "type": "wireframe",
            "response": {
                "figma_link": "https://...",
                "editable": true,
                "description": "..."
            }
        }
    """
    try:
        # Invoke Wireframe workflow
        result = wireframe_graph.invoke({"user_message": req.message})
        return {"type": "wireframe", "response": result["response"]}

    except Exception as e:
        print("WIREFRAME ERROR FROM MAIN.PY: ", e)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating wireframe: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
