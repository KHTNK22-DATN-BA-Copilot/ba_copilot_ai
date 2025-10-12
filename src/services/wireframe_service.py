"""
Wireframe generation service using LangGraph workflows.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
from services.llm_service import get_llm_service

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
            llm_service = get_llm_service()
            
            # Generate wireframe using LLM workflow
            wireframe_content = await llm_service.generate_wireframe(
                description=description,
                user_id=user_id,
                project_id=project_id
            )
            
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
            logger.error(f"Error generating wireframe: {str(e)}")
            raise Exception(f"Failed to generate wireframe: {str(e)}")
    
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