"""
Pydantic schemas for SRS (Software Requirements Specification) endpoints.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class SRSGenerateRequest(BaseModel):
    """Request schema for SRS generation."""
    
    project_input: str = Field(
        ..., 
        min_length=10,
        max_length=10000,
        description="Project description or requirements input for SRS generation"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_input": "Create a web-based math learning game for elementary school students with interactive exercises, progress tracking, and teacher dashboard."
            }
        }


class SRSGenerateResponse(BaseModel):
    """Response schema for SRS generation."""
    
    document_id: str = Field(..., description="Unique identifier for the generated document")
    user_id: Optional[str] = Field(None, description="User ID who generated the document")
    generated_at: str = Field(..., description="Timestamp when document was generated")
    input_description: str = Field(..., description="Original input used for generation")
    document: Dict[str, Any] = Field(..., description="Generated SRS document in JSON format")
    status: str = Field(..., description="Generation status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user123",
                "generated_at": "2024-01-01T12:00:00.000000",
                "input_description": "Math learning web game",
                "document": {
                    "title": "Math Learning Web Game",
                    "version": "1.0",
                    "author": "BA Copilot AI",
                    "project_overview": "Interactive web-based math learning platform",
                    "functional_requirements": ["User registration", "Interactive exercises"],
                    "non_functional_requirements": ["High performance", "Security"]
                },
                "status": "generated"  # Changed from "completed" to match database constraint
            }
        }


class SRSErrorResponse(BaseModel):
    """Error response schema for SRS operations."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: str = Field(..., description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Generation failed",
                "detail": "Invalid input provided",
                "timestamp": "2024-01-01T12:00:00.000000"
            }
        }