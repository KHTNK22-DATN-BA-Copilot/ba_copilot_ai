"""
SRS document endpoints.
"""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional
import uuid
import logging
import json

from schemas.srs import SRSGenerateRequest, SRSGenerateResponse, SRSErrorResponse
from services.srs_service import srs_service
from shared.error_handler import ValidationError
from shared.endpoint_helpers import raise_ai_friendly_http_exception

logger = logging.getLogger(__name__)
router = APIRouter()

class SRSDocument(BaseModel):
    """SRS document model."""
    document_id: str
    project_name: str
    content: str
    metadata: Dict[str, Any]

class SRSExportResponse(BaseModel):
    """SRS export response model."""
    download_url: str
    expires_at: str
    file_size_bytes: int
    format: str


@router.post("/generate", response_model=SRSGenerateResponse)
async def generate_srs_document(request: SRSGenerateRequest):
    """
    Generate a new SRS document using AI.

    Args:
        request: SRS generation request containing project input

    Returns:
        Generated SRS document with metadata

    Raises:
        HTTPException: If generation fails or input is invalid
    """
    try:
        logger.info("Received SRS generation request")

        # Validate input
        if not await srs_service.validate_input(request.project_input):
            error_response = ValidationError.invalid_input(
                "project_input",
                "Mô tả dự án phải có ít nhất 10 ký tự",
                request.project_input[:50] if request.project_input else ""
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_response
            )

        # Generate SRS document
        result = await srs_service.generate_srs(
            project_input=request.project_input,
            user_id=None  # TODO: Extract from JWT token when auth is implemented
        )

        logger.info(f"Successfully generated SRS document: {result['document_id']}")
        return SRSGenerateResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating SRS document: {str(e)}")
        raise_ai_friendly_http_exception(
            e,
            default_message="Không thể tạo tài liệu SRS"
        )


@router.get("/{document_id}", response_model=SRSDocument)
async def get_srs_document(document_id: str):
    """
    Retrieve a previously generated SRS document.
    
    Args:
        document_id: The unique identifier for the SRS document
    
    Returns:
        SRS document with content and metadata
    """
    # Mock SRS document data
    mock_content = """# Software Requirements Specification

## 1. Introduction

This document describes the software requirements for the E-commerce Platform project.

## 2. Overall Description

The E-commerce Platform is a comprehensive web-based application designed to provide 
a complete online shopping experience for customers and administrative tools for merchants.

## 3. System Requirements

### 3.1 Functional Requirements
- User registration and authentication
- Product catalog management
- Shopping cart functionality
- Payment processing
- Order management

### 3.2 Non-Functional Requirements
- Performance: Response time < 2 seconds
- Security: HTTPS encryption required
- Scalability: Support 10,000 concurrent users
"""
    
    if not document_id.startswith("doc_"):
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    
    return SRSDocument(
        document_id=document_id,
        project_name="E-commerce Platform",
        content=mock_content,
        metadata={
            "created_at": "2025-09-20T14:30:00Z",
            "updated_at": "2025-09-20T14:30:00Z",
            "template_used": "standard",
            "status": "generated",
            "word_count": 150,
            "sections": 3
        }
    )

@router.get("/{document_id}/export", response_model=SRSExportResponse)
async def export_srs_document(
    document_id: str,
    format: str = Query(..., description="Export format (md, pdf, html)"),
    include_metadata: bool = Query(False, description="Include metadata in export"),
    include_diagrams: bool = Query(True, description="Include generated diagrams")
):
    """
    Export SRS document in specified format.
    
    Args:
        document_id: The unique identifier for the SRS document
        format: Export format (md, pdf, html)
        include_metadata: Whether to include metadata
        include_diagrams: Whether to include diagrams
    
    Returns:
        Export download information
    """
    if not document_id.startswith("doc_"):
        raise HTTPException(status_code=400, detail="Invalid document ID format")
        
    if format not in ["md", "pdf", "html"]:
        raise HTTPException(status_code=400, detail="Invalid format. Supported: md, pdf, html")
    
    file_sizes = {"md": 15360, "pdf": 245760, "html": 34560}
    
    return SRSExportResponse(
        download_url=f"http://localhost:8000/exports/{document_id}.{format}",
        expires_at="2025-09-21T14:30:00Z",
        file_size_bytes=file_sizes.get(format, 15360),
        format=format
    )