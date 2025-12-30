# models/metadata_extraction.py
"""
Metadata Extraction Models

This module defines Pydantic models for the metadata extraction feature,
which analyzes uploaded documents to detect which BA document types are present
and extracts their line ranges.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict


# ============================================================================
# Phase-based Document Type Groupings
# ============================================================================

# Phase 1: Project Initiation
PHASE_1_PROJECT_INITIATION = [
    "stakeholder-register",
    "high-level-requirements",
    "requirements-management-plan",
]

# Phase 2: Business Planning
PHASE_2_BUSINESS_PLANNING = [
    "business-case",
    "scope-statement",
    "product-roadmap",
]

# Phase 3: Feasibility & Risk Analysis
PHASE_3_FEASIBILITY_RISK = [
    "feasibility-study",
    "cost-benefit-analysis",
    "risk-register",
    "compliance",
]

# Phase 4: High-Level Design
PHASE_4_HIGH_LEVEL_DESIGN = [
    "hld-arch",
    "hld-cloud",
    "hld-tech",
]

# Phase 5: Low-Level Design
PHASE_5_LOW_LEVEL_DESIGN = [
    "lld-arch",
    "lld-db",
    "lld-api",
    "lld-pseudo",
]

# Phase 6: UI/UX Design
PHASE_6_UIUX_DESIGN = [
    "uiux-wireframe",
    "uiux-mockup",
    "uiux-prototype",
]

# Phase 7: Testing & QA
PHASE_7_TESTING_QA = [
    "rtm",
]

# Additional Document Types (SRS, Diagrams)
ADDITIONAL_DOCUMENT_TYPES = [
    "srs",
    "class-diagram",
    "usecase-diagram",
    "activity-diagram",
    "wireframe",
]

# Complete list of all document types (26 total)
ALL_DOCUMENT_TYPES = (
    PHASE_1_PROJECT_INITIATION
    + PHASE_2_BUSINESS_PLANNING
    + PHASE_3_FEASIBILITY_RISK
    + PHASE_4_HIGH_LEVEL_DESIGN
    + PHASE_5_LOW_LEVEL_DESIGN
    + PHASE_6_UIUX_DESIGN
    + PHASE_7_TESTING_QA
    + ADDITIONAL_DOCUMENT_TYPES
)


# ============================================================================
# Document Type Descriptions for LLM Prompts
# ============================================================================

DOCUMENT_TYPE_DESCRIPTIONS = {
    # Phase 1: Project Initiation
    "stakeholder-register": "A register listing all project stakeholders with their roles, interests, and contact information",
    "high-level-requirements": "High-level functional and non-functional requirements of the system",
    "requirements-management-plan": "Plan for managing requirements throughout the project lifecycle",
    
    # Phase 2: Business Planning
    "business-case": "Document justifying the project with cost-benefit analysis and strategic alignment",
    "scope-statement": "Detailed description of project scope, boundaries, deliverables, and constraints",
    "product-roadmap": "Timeline showing planned features and releases over multiple phases",
    
    # Phase 3: Feasibility & Risk Analysis
    "feasibility-study": "Analysis of technical, economic, and operational feasibility of the project",
    "cost-benefit-analysis": "Financial analysis comparing project costs against expected benefits",
    "risk-register": "List of identified risks with impact, probability, and mitigation strategies",
    "compliance": "Compliance requirements and regulatory constraints checklist",
    
    # Phase 4: High-Level Design
    "hld-arch": "High-level system architecture showing major components and their interactions",
    "hld-cloud": "Cloud infrastructure design including deployment architecture",
    "hld-tech": "Technology stack selection and justification document",
    
    # Phase 5: Low-Level Design
    "lld-arch": "Detailed component-level architecture and design patterns",
    "lld-db": "Database schema design with tables, relationships, and indexes",
    "lld-api": "API specifications with endpoints, request/response formats, and authentication",
    "lld-pseudo": "Pseudocode or algorithmic descriptions of key components",
    
    # Phase 6: UI/UX Design
    "uiux-wireframe": "Low-fidelity wireframes showing page layouts and navigation flow",
    "uiux-mockup": "High-fidelity visual designs with colors, typography, and branding",
    "uiux-prototype": "Interactive prototype specifications or descriptions",
    
    # Phase 7: Testing & QA
    "rtm": "Requirements Traceability Matrix linking requirements to test cases",
    
    # Additional
    "srs": "Software Requirements Specification - comprehensive functional and non-functional requirements",
    "class-diagram": "UML class diagram showing system classes and relationships",
    "usecase-diagram": "UML use case diagram showing actors and system interactions",
    "activity-diagram": "UML activity diagram showing workflow or process flow",
    "wireframe": "UI wireframe or layout design",
}


# ============================================================================
# Pydantic Models
# ============================================================================

class DocumentTypeMetadata(BaseModel):
    """
    Metadata for a single document type detection result.
    
    Attributes:
        type: The document type identifier (e.g., 'business-case')
        line_start: Starting line number (1-indexed), -1 if not found
        line_end: Ending line number (1-indexed), -1 if not found
    """
    type: str = Field(..., description="Document type identifier")
    line_start: int = Field(..., description="Starting line number (1-indexed), -1 if not found")
    line_end: int = Field(..., description="Ending line number (1-indexed), -1 if not found")


class MetadataExtractionRequest(BaseModel):
    """
    Request model for metadata extraction.
    
    Attributes:
        document_id: UUID of the document
        content: Markdown content to analyze
        filename: Optional filename for context
    """
    document_id: str = Field(..., description="UUID of the document")
    content: str = Field(..., description="Markdown content to analyze")
    filename: Optional[str] = Field(None, description="Optional filename for context")


class MetadataExtractionResponse(BaseModel):
    """
    Response model for metadata extraction.
    
    Attributes:
        document_id: UUID of the document
        type: Response type (always 'metadata_extraction')
        response: List of document type detection results
    """
    document_id: str = Field(..., description="UUID of the document")
    type: str = Field(default="metadata_extraction", description="Response type")
    response: List[DocumentTypeMetadata] = Field(
        ..., 
        description="List of document type detection results"
    )


# ============================================================================
# Helper Functions
# ============================================================================

def create_empty_metadata_response(document_id: str) -> MetadataExtractionResponse:
    """
    Create a metadata response with all document types marked as not found.
    
    Args:
        document_id: The document UUID
        
    Returns:
        MetadataExtractionResponse with all types having -1 line ranges
    """
    return MetadataExtractionResponse(
        document_id=document_id,
        type="metadata_extraction",
        response=[
            DocumentTypeMetadata(type=dt, line_start=-1, line_end=-1)
            for dt in ALL_DOCUMENT_TYPES
        ]
    )


def create_single_type_metadata(
    document_id: str,
    doc_type: str,
    line_start: int,
    line_end: int
) -> MetadataExtractionResponse:
    """
    Create a metadata response with one document type detected.
    
    Args:
        document_id: The document UUID
        doc_type: The detected document type
        line_start: Starting line number
        line_end: Ending line number
        
    Returns:
        MetadataExtractionResponse with specified type detected, others as -1
    """
    response_items = []
    for dt in ALL_DOCUMENT_TYPES:
        if dt == doc_type:
            response_items.append(
                DocumentTypeMetadata(type=dt, line_start=line_start, line_end=line_end)
            )
        else:
            response_items.append(
                DocumentTypeMetadata(type=dt, line_start=-1, line_end=-1)
            )
    
    return MetadataExtractionResponse(
        document_id=document_id,
        type="metadata_extraction",
        response=response_items
    )
