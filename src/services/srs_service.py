"""
SRS (Software Requirements Specification) Service.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
from services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class SRSService:
    """Service for generating Software Requirements Specification documents."""
    
    def __init__(self):
        """Initialize the SRS service."""
        logger.info("SRS Service initialized")
    
    async def generate_srs(self, project_input: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive SRS document.
        
        Args:
            project_input: Input requirements/description from user
            user_id: Optional user ID for tracking
            
        Returns:
            Dict containing the generated SRS document with metadata
        """
        try:
            logger.info(f"Generating SRS document for user: {user_id}")
            
            # Get LLM service instance
            llm_service = get_llm_service()
            
            # Generate SRS document using LLM
            srs_content = await llm_service.generate_srs_document(project_input)
            
            # Add metadata
            document_id = str(uuid4())
            generated_at = datetime.utcnow().isoformat()
            
            # Prepare response
            response = {
                "document_id": document_id,
                "user_id": user_id,
                "generated_at": generated_at,
                "input_description": project_input,
                "document": srs_content,
                "status": "completed"
            }
            
            logger.info(f"Successfully generated SRS document {document_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating SRS document: {str(e)}")
            raise Exception(f"Failed to generate SRS document: {str(e)}")
    
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