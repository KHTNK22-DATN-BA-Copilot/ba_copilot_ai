"""
SRS (Software Requirements Specification) Service.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
from services.llm_service import get_llm_service
from shared.error_handler import (
    ValidationError,
    LLMServiceError,
    InternalError
)

logger = logging.getLogger(__name__)


class SRSService:
    """Service for generating Software Requirements Specification documents."""
    
    def __init__(self):
        """Initialize the SRS service."""
        logger.info("SRS Service initialized")
    
    async def generate_srs(self, project_input: str, user_id: Optional[str] = None, project_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive SRS document.

        Args:
            project_input: Input requirements/description from user
            user_id: Optional user ID for tracking
            project_id: Optional project ID for organization

        Returns:
            Dict containing the generated SRS document with metadata

        Raises:
            Exception: With AI-friendly error details
        """
        try:
            logger.info(f"Generating SRS document for user: {user_id}, project: {project_id}")

            # Get LLM service instance
            try:
                llm_service = get_llm_service()
            except Exception as e:
                error_response = LLMServiceError.provider_unavailable("LLM Service", e)
                raise Exception(str(error_response))

            # Generate SRS document using LLM with LangGraph workflow
            try:
                srs_content = await llm_service.generate_srs_document(
                    user_input=project_input,
                    user_id=user_id,
                    project_id=project_id
                )
            except Exception as e:
                error_response = LLMServiceError.generation_failed("tài liệu SRS", e)
                raise Exception(str(error_response))

            # Add metadata
            document_id = str(uuid4())
            generated_at = datetime.utcnow().isoformat()

            # Prepare response
            response = {
                "document_id": document_id,
                "user_id": user_id,
                "project_id": project_id,
                "generated_at": generated_at,
                "input_description": project_input,
                "document": srs_content,
                "status": "completed"
            }

            logger.info(f"Successfully generated SRS document {document_id}")
            return response

        except Exception as e:
            # Check if it's already a formatted error
            error_str = str(e)
            if "error_id" in error_str:
                # Already formatted, just re-raise
                raise
            else:
                # Unexpected error, wrap it
                error_response = InternalError.unexpected_error("tạo tài liệu SRS", e)
                logger.error(f"Unexpected error in generate_srs: {error_response}")
                raise Exception(str(error_response))
    
    async def validate_input(self, project_input: str) -> bool:
        """
        Validate input for SRS generation.
        
        Args:
            project_input: Input to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not project_input or not project_input.strip():
            return False
        
        if len(project_input.strip()) < 10:
            return False
            
        return True


# Global instance
srs_service = SRSService()