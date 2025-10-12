"""
LLM Service using LangGraph workflows for advanced AI processing.
"""

from datetime import datetime
import json
import logging
from typing import Dict, Any, Optional
from core.config import settings
from .workflows.srs_workflow import SRSWorkflow

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with LLMs using LangGraph workflows."""
    
    def __init__(self):
        """Initialize the LLM service with LangGraph workflows."""
        self.srs_workflow = None
        self._initialized = False
        
    def _ensure_initialized(self):
        """Ensure the LLM service is initialized."""
        if not self._initialized:
            try:
                # Initialize SRS workflow
                self.srs_workflow = SRSWorkflow()
                self._initialized = True
                logger.info("LLM Service initialized with LangGraph workflows")
            except Exception as e:
                logger.error(f"Failed to initialize LLM Service: {e}")
                # Continue with fallback mode
                self._initialized = True
                logger.info("LLM Service initialized in fallback mode")
    
    async def generate_srs_document(
        self, 
        user_input: str, 
        user_id: Optional[str] = None,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate SRS document using LangGraph workflow.
        
        Args:
            user_input: Input requirements from frontend
            user_id: Optional user ID for tracking
            project_id: Optional project ID for organization
            
        Returns:
            Dict containing the generated SRS document in JSON format
        """
        try:
            self._ensure_initialized()
            
            logger.info(f"Generating SRS document using LangGraph workflow for input: {user_input[:100]}...")
            
            if self.srs_workflow:
                # Use LangGraph workflow for comprehensive SRS generation
                srs_document = await self.srs_workflow.generate_srs_document(
                    project_input=user_input,
                    user_id=user_id,
                    project_id=project_id
                )
                logger.info("Successfully generated SRS document using LangGraph workflow")
                return srs_document
            else:
                # Fallback: construct a structured response without workflows
                logger.warning("SRS workflow not available, using fallback generation")
                current_date_string = datetime.now().strftime('%Y-%m-%d')
                return {
                    "title": "Generated SRS Document (Fallback)",
                    "version": "1.0",
                    "date": current_date_string,
                    "author": "BA Copilot AI",
                    "project_overview": user_input,
                    "functional_requirements": ["Requirements based on: " + user_input],
                    "non_functional_requirements": ["Performance and security requirements to be defined"],
                    "system_architecture": "Architecture to be defined based on requirements",
                    "user_stories": ["User story derived from: " + user_input],
                    "constraints": ["Technical constraints to be identified"],
                    "assumptions": ["Assumptions to be validated"],
                    "glossary": {"SRS": "Software Requirements Specification"},
                    "metadata": {
                        "user_id": user_id,
                        "project_id": project_id,
                        "provider": "fallback"
                    }
                }
                
        except Exception as e:
            # On any unexpected error, return fallback instead of 500
            logger.error(f"Error generating SRS document: {str(e)}")
            current_date_string = datetime.now().strftime('%Y-%m-%d')
            return {
                "title": "Generated SRS Document (Error Fallback)",
                "version": "1.0",
                "date": current_date_string,
                "author": "BA Copilot AI",
                "project_overview": user_input,
                "functional_requirements": ["Requirements based on: " + user_input],
                "non_functional_requirements": ["Performance and security requirements to be defined"],
                "system_architecture": "Architecture to be defined based on requirements",
                "user_stories": ["User story derived from: " + user_input],
                "constraints": ["Technical constraints to be identified"],
                "assumptions": ["Assumptions to be validated"],
                "glossary": {"SRS": "Software Requirements Specification"},
                "metadata": {
                    "user_id": user_id,
                    "project_id": project_id,
                    "provider": "error_fallback",
                    "error": str(e)
                }
            }
    
    async def generate_content(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        user_id: Optional[str] = None
    ) -> str:
        """
        Generate content using available LLM providers.
        
        Args:
            prompt: User prompt
            temperature: Response creativity (0.0 to 1.0)
            user_id: Optional user ID for tracking
            
        Returns:
            Generated content as string
        """
        try:
            self._ensure_initialized()
            
            logger.info(f"Generating content for user {user_id}: {prompt[:50]}...")
            
            # For now, use a simple text generation approach
            # This can be extended with additional LangGraph workflows for other content types
            
            # Placeholder for content generation workflow
            logger.info("Content generation workflow - placeholder implementation")
            
            # Try to use SRS workflow's LLM if available
            if self.srs_workflow and hasattr(self.srs_workflow, 'llm') and self.srs_workflow.llm:
                try:
                    from langchain_core.messages import HumanMessage
                    response = await self.srs_workflow.llm.ainvoke([HumanMessage(content=prompt)])
                    content = response.content
                    return str(content) if content else prompt
                except Exception as e:
                    logger.warning(f"LLM content generation failed: {e}")
                    return f"Generated content based on: {prompt}"
            else:
                # Simple fallback content generation
                return f"Generated content based on: {prompt}"
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return f"Content generation error. Original prompt: {prompt}"

    async def generate_wireframe(
        self, 
        description: str, 
        user_id: Optional[str] = None,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate wireframe using LangGraph workflow (placeholder).
        
        Args:
            description: Wireframe description
            user_id: Optional user ID
            project_id: Optional project ID
            
        Returns:
            Generated wireframe data
        """
        logger.info("Wireframe generation workflow - placeholder implementation")
        
        # Placeholder for wireframe generation workflow
        return {
            "wireframe_id": f"wireframe_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": "Generated Wireframe",
            "description": description,
            "html_content": f"<div>Wireframe based on: {description}</div>",
            "css_content": "/* CSS to be generated */",
            "metadata": {
                "user_id": user_id,
                "project_id": project_id,
                "generated_at": datetime.now().isoformat()
            }
        }

    async def generate_diagram(
        self, 
        description: str, 
        diagram_type: str,
        user_id: Optional[str] = None,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate diagram using LangGraph workflow (placeholder).
        
        Args:
            description: Diagram description
            diagram_type: Type of diagram (sequence, architecture, usecase, flowchart)
            user_id: Optional user ID
            project_id: Optional project ID
            
        Returns:
            Generated diagram data
        """
        logger.info(f"Diagram generation workflow - {diagram_type} - placeholder implementation")
        
        # Placeholder for diagram generation workflow
        return {
            "diagram_id": f"diagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "diagram_type": diagram_type,
            "title": f"Generated {diagram_type.title()} Diagram",
            "description": description,
            "mermaid_code": f"graph TD\n    A[Start] --> B[{description}]\n    B --> C[End]",
            "metadata": {
                "user_id": user_id,
                "project_id": project_id,
                "generated_at": datetime.now().isoformat()
            }
        }

    async def process_conversation(
        self, 
        message: str, 
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process conversation message using LangGraph workflow (placeholder).
        
        Args:
            message: User message
            conversation_id: Optional conversation ID
            user_id: Optional user ID
            project_id: Optional project ID
            
        Returns:
            AI response data
        """
        logger.info("Conversation processing workflow - placeholder implementation")
        
        # Placeholder for conversation processing workflow
        return {
            "message_id": f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "conversation_id": conversation_id or f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "role": "assistant",
            "content": f"AI response to: {message}",
            "metadata": {
                "user_id": user_id,
                "project_id": project_id,
                "generated_at": datetime.now().isoformat()
            }
        }


# Global instance - initialized lazily
_llm_service_instance: Optional[LLMService] = None

def get_llm_service() -> LLMService:
    """Get or create the global LLM service instance."""
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance

# Backwards compatibility
llm_service = get_llm_service()