"""
Wireframe generation service using LangGraph workflows.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
from services.llm_service import get_llm_service
from shared.error_handler import (
    LLMServiceError,
    InternalError
)

logger = logging.getLogger(__name__)


class WireframeService:
    """Service for generating wireframe prototypes."""
    
    def __init__(self):
        """Initialize the wireframe service."""
        logger.info("Wireframe Service initialized")
    
    async def generate_wireframe(
        self, 
        description: str, 
        user_id: Optional[str] = None,
        project_id: Optional[int] = None,
        template_type: str = "standard"
    ) -> Dict[str, Any]:
        """
        Generate a wireframe prototype.
        
        Args:
            description: Wireframe description/requirements
            user_id: Optional user ID for tracking
            project_id: Optional project ID for organization
            template_type: Wireframe template type
            
        Returns:
            Dict containing the generated wireframe with metadata
        """
        try:
            logger.info(f"Generating wireframe for user: {user_id}, project: {project_id}")

            # Get LLM service instance
            try:
                llm_service = get_llm_service()
            except Exception as e:
                error_response = LLMServiceError.provider_unavailable("LLM Service", e)
                raise Exception(str(error_response))

            # Generate wireframe using LLM workflow
            try:
                wireframe_content = await llm_service.generate_wireframe(
                    description=description,
                    user_id=user_id,
                    project_id=project_id
                )
            except Exception as e:
                error_response = LLMServiceError.generation_failed("wireframe", e)
                raise Exception(str(error_response))

            # Add metadata
            wireframe_id = str(uuid4())
            generated_at = datetime.utcnow().isoformat()

            # Prepare response
            response = {
                "wireframe_id": wireframe_id,
                "user_id": user_id,
                "project_id": project_id,
                "generated_at": generated_at,
                "description": description,
                "template_type": template_type,
                "wireframe": wireframe_content,
                "status": "completed"
            }

            logger.info(f"Successfully generated wireframe {wireframe_id}")
            return response

        except Exception as e:
            # Check if it's already a formatted error
            error_str = str(e)
            if "error_id" in error_str:
                raise
            else:
                error_response = InternalError.unexpected_error("tạo wireframe", e)
                logger.error(f"Unexpected error in generate_wireframe: {error_response}")
                raise Exception(str(error_response))
    
    async def validate_input(self, description: str) -> bool:
        """
        Validate input for wireframe generation.
        
        Args:
            description: Input to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not description or not description.strip():
            return False
        
        if len(description.strip()) < 5:
            return False
            
        return True


# Global instance
wireframe_service = WireframeService()