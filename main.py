# ai_service/main.py
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from workflows import srs_graph, class_diagram_graph, usecase_diagram_graph, activity_diagram_graph, wireframe_graph
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

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
    content_id: Optional[str] = None
    inputFile: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Create SRS for hotel management system",
                "content_id": "123e4567-e89b-12d3-a456-426614174000"
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
async def generate_srs(
    message: str = Form(...),
    content_id: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    """
    Generate Software Requirements Specification (SRS) document.

    Args:
        message: User message/requirement description
        content_id: Optional ID of the content for chat history
        files: Optional list of files to process (images, PDFs, DOCX, TXT)

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
        # Prepare state for workflow
        state = {
            "user_message": message,
            "content_id": content_id,
            "files": files or []
        }

        # Invoke SRS workflow
        result = srs_graph.invoke(state)
        return {"type": "srs", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating SRS: {str(e)}"
        )

@app.post("/api/v1/generate/class-diagram")
async def generate_class_diagram(
    message: str = Form(...),
    content_id: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    """
    Generate UML Class Diagram in Mermaid markdown format.

    Args:
        message: User message/requirement description
        content_id: Optional ID of the content for chat history
        files: Optional list of files to process (images, PDFs, DOCX, TXT)

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
        # Prepare state for workflow
        state = {
            "user_message": message,
            "content_id": content_id,
            "files": files or []
        }

        # Invoke Class Diagram workflow
        result = class_diagram_graph.invoke(state)
        return {"type": "diagram", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating class diagram: {str(e)}"
        )

@app.post("/api/v1/generate/usecase-diagram")
async def generate_usecase_diagram(
    message: str = Form(...),
    content_id: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    """
    Generate UML Use Case Diagram in Mermaid markdown format.

    Args:
        message: User message/requirement description
        content_id: Optional ID of the content for chat history
        files: Optional list of files to process (images, PDFs, DOCX, TXT)

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
        # Prepare state for workflow
        state = {
            "user_message": message,
            "content_id": content_id,
            "files": files or []
        }

        # Invoke Use Case Diagram workflow
        result = usecase_diagram_graph.invoke(state)
        return {"type": "diagram", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating use case diagram: {str(e)}"
        )

@app.post("/api/v1/generate/activity-diagram")
async def generate_activity_diagram(
    message: str = Form(...),
    content_id: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    """
    Generate UML Activity Diagram in Mermaid markdown format.

    Args:
        message: User message/requirement description
        content_id: Optional ID of the content for chat history
        files: Optional list of files to process (images, PDFs, DOCX, TXT)

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
        # Prepare state for workflow
        state = {
            "user_message": message,
            "content_id": content_id,
            "files": files or []
        }

        # Invoke Activity Diagram workflow
        result = activity_diagram_graph.invoke(state)
        return {"type": "diagram", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating activity diagram: {str(e)}"
        )


@app.post("/api/v1/wireframe/generate")
async def generate_wireframe(
    message: str = Form(...),
    content_id: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    """
    Generate wireframe/UI mockup.

    Args:
        message: User message/requirement description
        content_id: Optional ID of the content for chat history
        files: Optional list of files to process (images, PDFs, DOCX, TXT)

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
        # Prepare state for workflow
        state = {
            "user_message": message,
            "content_id": content_id,
            "files": files or []
        }

        # Invoke Wireframe workflow
        result = wireframe_graph.invoke(state)
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
