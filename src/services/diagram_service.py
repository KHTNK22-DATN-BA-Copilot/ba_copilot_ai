"""
Diagram generation service using LangGraph workflows.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
from services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class DiagramService:
    """Service for generating various types of diagrams."""
    
    def __init__(self):
        """Initialize the diagram service."""
        logger.info("Diagram Service initialized")
    
    async def generate_diagram(
        self, 
        description: str, 
        diagram_type: str,
        user_id: Optional[str] = None,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a diagram.
        
        Args:
            description: Diagram description/requirements
            diagram_type: Type of diagram (sequence, architecture, usecase, flowchart)
            user_id: Optional user ID for tracking
            project_id: Optional project ID for organization
            
        Returns:
            Dict containing the generated diagram with metadata
        """
        try:
            logger.info(f"Generating {diagram_type} diagram for user: {user_id}, project: {project_id}")
            
            # Validate diagram type
            valid_types = ["sequence", "architecture", "usecase", "flowchart"]
            if diagram_type not in valid_types:
                raise ValueError(f"Invalid diagram type. Must be one of: {valid_types}")
            
            # Get LLM service instance
            llm_service = get_llm_service()
            
            # Generate diagram using LLM workflow
            diagram_content = await llm_service.generate_diagram(
                description=description,
                diagram_type=diagram_type,
                user_id=user_id,
                project_id=project_id
            )
            
            # Add metadata
            diagram_id = str(uuid4())
            generated_at = datetime.utcnow().isoformat()
            
            # Prepare response
            response = {
                "diagram_id": diagram_id,
                "user_id": user_id,
                "project_id": project_id,
                "generated_at": generated_at,
                "description": description,
                "diagram_type": diagram_type,
                "diagram": diagram_content,
                "status": "completed"
            }
            
            logger.info(f"Successfully generated {diagram_type} diagram {diagram_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating {diagram_type} diagram: {str(e)}")
            raise Exception(f"Failed to generate {diagram_type} diagram: {str(e)}")
    
    async def validate_input(self, description: str, diagram_type: str) -> bool:
        """
        Validate input for diagram generation.
        
        Args:
            description: Input to validate
            diagram_type: Diagram type to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not description or not description.strip():
            return False
        
        if len(description.strip()) < 5:
            return False
        
        valid_types = ["sequence", "architecture", "usecase", "flowchart"]
        if diagram_type not in valid_types:
            return False
            
        return True


# Global instance
diagram_service = DiagramService()