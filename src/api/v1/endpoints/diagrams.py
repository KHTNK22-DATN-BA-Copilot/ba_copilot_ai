"""
Diagram endpoints.
"""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid
import logging

from services.diagram_service import diagram_service
from shared.error_handler import ValidationError
from shared.endpoint_helpers import raise_ai_friendly_http_exception

logger = logging.getLogger(__name__)
router = APIRouter()


class DiagramGenerateRequest(BaseModel):
    """Diagram generation request model."""
    description: str
    diagram_type: str  # sequence, architecture, usecase, flowchart
    project_id: Optional[int] = None


class DiagramGenerateResponse(BaseModel):
    """Diagram generation response model."""
    diagram_id: str
    user_id: Optional[str]
    project_id: Optional[int]
    generated_at: str
    description: str
    diagram_type: str
    diagram: Dict[str, Any]
    status: str


class DiagramResponse(BaseModel):
    """Diagram response model."""
    diagram_id: str
    type: str
    title: str
    mermaid_code: str
    preview_url: str
    metadata: Dict[str, Any]

class DiagramExportResponse(BaseModel):
    """Diagram export response model."""
    download_url: str
    expires_at: str
    file_size_bytes: int
    format: str
    quality: Optional[str] = None
    theme: Optional[str] = None

class DiagramListResponse(BaseModel):
    """Diagram list response model."""
    diagrams: List[Dict[str, Any]]
    total_count: int
    has_next: bool


@router.post("/generate", response_model=DiagramGenerateResponse)
async def generate_diagram(request: DiagramGenerateRequest):
    """
    Generate a new diagram using AI.
    
    Args:
        request: Diagram generation request containing description and type
    
    Returns:
        Generated diagram with metadata
    
    Raises:
        HTTPException: If generation fails or input is invalid
    """
    try:
        logger.info(f"Received {request.diagram_type} diagram generation request")

        # Validate input
        if not await diagram_service.validate_input(request.description, request.diagram_type):
            error_response = ValidationError.invalid_input(
                "description hoặc diagram_type",
                "Mô tả phải có ít nhất 5 ký tự và loại sơ đồ phải hợp lệ (sequence, architecture, usecase, flowchart)",
                f"{request.description[:30]}... | type: {request.diagram_type}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_response
            )

        # Generate diagram
        result = await diagram_service.generate_diagram(
            description=request.description,
            diagram_type=request.diagram_type,
            user_id=None,  # TODO: Extract from JWT token when auth is implemented
            project_id=request.project_id
        )

        logger.info(f"Successfully generated {request.diagram_type} diagram: {result['diagram_id']}")
        return DiagramGenerateResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating {request.diagram_type} diagram: {str(e)}")
        raise_ai_friendly_http_exception(
            e,
            default_message=f"Không thể tạo sơ đồ {request.diagram_type}"
        )

@router.get("/{diagram_id}", response_model=DiagramResponse)
async def get_diagram(diagram_id: str):
    """
    Retrieve a generated diagram.
    
    Args:
        diagram_id: The unique identifier for the diagram
    
    Returns:
        Diagram with Mermaid code, preview URL, and metadata
    """
    if not diagram_id.startswith("diag_"):
        raise HTTPException(status_code=400, detail="Invalid diagram ID format")
    
    # Mock Mermaid code based on diagram type
    diagram_type = "sequence"  # Extract from ID in real implementation
    
    mock_mermaid_codes = {
        "sequence": """sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant D as Database
    participant A as Auth Service
    
    U->>F: Enter credentials
    F->>B: POST /auth/login
    B->>A: Validate credentials
    A->>D: Check user data
    D-->>A: User found
    A-->>B: Return JWT token
    B-->>F: Authentication successful
    F-->>U: Redirect to dashboard
    
    Note over U,A: Authentication Flow Complete""",
        
        "architecture": """graph TD
    A[User Interface] --> B[API Gateway]
    B --> C[Authentication Service]
    B --> D[Business Logic Layer]
    D --> E[Data Access Layer]
    E --> F[(Database)]
    D --> G[External APIs]
    C --> H[Identity Provider]
    
    style A fill:#e1f5fe
    style F fill:#c8e6c9
    style H fill:#fff3e0""",
        
        "flowchart": """flowchart TD
    A([Start: User Login Request]) --> B{Valid Credentials?}
    B -->|Yes| C[Generate JWT Token]
    B -->|No| D[Return Error Message]
    C --> E[Store Session]
    E --> F[Send Success Response]
    F --> G([End: User Authenticated])
    D --> H([End: Authentication Failed])
    
    style A fill:#c8e6c9
    style G fill:#c8e6c9
    style H fill:#ffcdd2"""
    }
    
    return DiagramResponse(
        diagram_id=diagram_id,
        type=diagram_type,
        title="User Authentication Flow",
        mermaid_code=mock_mermaid_codes.get(diagram_type, mock_mermaid_codes["sequence"]),
        preview_url=f"http://localhost:8000/v1/diagrams/{diagram_id}/preview",
        metadata={
            "created_at": "2025-09-20T14:30:00Z",
            "updated_at": "2025-09-20T14:30:00Z",
            "status": "generated",
            "complexity": "medium",
            "actors_count": 5,
            "interactions_count": 8
        }
    )

@router.get("/{diagram_id}/export", response_model=DiagramExportResponse)
async def export_diagram(
    diagram_id: str,
    format: str = Query(..., description="Export format (svg, png, pdf, mermaid)"),
    quality: Optional[str] = Query("medium", description="Image quality (low, medium, high)"),
    theme: Optional[str] = Query("default", description="Diagram theme (default, dark, forest, neutral)")
):
    """
    Export diagram in specified format.
    
    Args:
        diagram_id: The unique identifier for the diagram
        format: Export format (svg, png, pdf, mermaid)
        quality: Image quality for raster formats
        theme: Diagram theme
    
    Returns:
        Export download information
    """
    if not diagram_id.startswith("diag_"):
        raise HTTPException(status_code=400, detail="Invalid diagram ID format")
        
    if format not in ["svg", "png", "pdf", "mermaid"]:
        raise HTTPException(status_code=400, detail="Invalid format. Supported: svg, png, pdf, mermaid")
    
    if quality and quality not in ["low", "medium", "high"]:
        raise HTTPException(status_code=400, detail="Invalid quality. Supported: low, medium, high")
        
    if theme and theme not in ["default", "dark", "forest", "neutral"]:
        raise HTTPException(status_code=400, detail="Invalid theme. Supported: default, dark, forest, neutral")
    
    file_sizes = {
        "svg": 12288, 
        "png": 51200, 
        "pdf": 81920, 
        "mermaid": 2048
    }
    
    return DiagramExportResponse(
        download_url=f"http://localhost:8000/exports/{diagram_id}.{format}",
        expires_at="2025-09-21T14:30:00Z",
        file_size_bytes=file_sizes.get(format, 12288),
        format=format,
        quality=quality,
        theme=theme
    )

@router.get("/", response_model=DiagramListResponse)
async def list_diagrams(
    type: Optional[str] = Query(None, description="Filter by diagram type"),
    limit: int = Query(20, ge=1, le=100, description="Maximum diagrams to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    search: Optional[str] = Query(None, description="Search in diagram titles")
):
    """
    List user's diagrams.
    
    Args:
        type: Filter by diagram type (sequence, architecture, usecase, flowchart)
        limit: Maximum diagrams to return (1-100)
        offset: Pagination offset
        search: Search term for diagram titles
    
    Returns:
        List of diagrams with pagination info
    """
    if type and type not in ["sequence", "architecture", "usecase", "flowchart"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid type. Supported: sequence, architecture, usecase, flowchart"
        )
    
    # Mock diagram data
    mock_diagrams = [
        {
            "diagram_id": "diag_550e8400-seq-001",
            "type": "sequence",
            "title": "User Authentication Flow",
            "created_at": "2025-09-20T14:30:00Z",
            "status": "generated"
        },
        {
            "diagram_id": "diag_550e8400-arch-001",
            "type": "architecture",
            "title": "System Architecture Overview",
            "created_at": "2025-09-19T10:15:00Z",
            "status": "generated"
        },
        {
            "diagram_id": "diag_550e8400-uc-001",
            "type": "usecase",
            "title": "E-commerce Use Cases",
            "created_at": "2025-09-18T16:45:00Z",
            "status": "generated"
        },
        {
            "diagram_id": "diag_550e8400-flow-001",
            "type": "flowchart",
            "title": "Order Processing Workflow",
            "created_at": "2025-09-17T09:20:00Z",
            "status": "generated"
        }
    ]
    
    # Apply filters
    filtered_diagrams = mock_diagrams
    if type:
        filtered_diagrams = [d for d in filtered_diagrams if d["type"] == type]
    
    if search:
        filtered_diagrams = [
            d for d in filtered_diagrams 
            if search.lower() in d["title"].lower()
        ]
    
    # Apply pagination
    total_count = len(filtered_diagrams)
    paginated_diagrams = filtered_diagrams[offset:offset + limit]
    has_next = offset + limit < total_count
    
    return DiagramListResponse(
        diagrams=paginated_diagrams,
        total_count=total_count,
        has_next=has_next
    )