"""
Conversation service using LangGraph workflows.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4
from services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing AI conversations."""
    
    def __init__(self):
        """Initialize the conversation service."""
        logger.info("Conversation Service initialized")
    
    async def send_message(
        self, 
        message: str, 
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send a message and get AI response.
        
        Args:
            message: User message
            conversation_id: Optional conversation ID
            user_id: Optional user ID for tracking
            project_id: Optional project ID for organization
            
        Returns:
            Dict containing the AI response with metadata
        """
        try:
            logger.info(f"Processing message for user: {user_id}, project: {project_id}")
            
            # Get LLM service instance
            llm_service = get_llm_service()
            
            # Process conversation using LLM workflow
            response_content = await llm_service.process_conversation(
                message=message,
                conversation_id=conversation_id,
                user_id=user_id,
                project_id=project_id
            )
            
            # Add metadata
            message_id = str(uuid4())
            generated_at = datetime.utcnow().isoformat()
            
            # Prepare response
            response = {
                "message_id": message_id,
                "conversation_id": conversation_id or str(uuid4()),
                "user_id": user_id,
                "project_id": project_id,
                "generated_at": generated_at,
                "user_message": message,
                "ai_response": response_content,
                "status": "completed"
            }
            
            logger.info(f"Successfully processed conversation message {message_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing conversation: {str(e)}")
            raise Exception(f"Failed to process conversation: {str(e)}")
    
    async def get_conversation_history(
        self, 
        conversation_id: str,
        user_id: Optional[str] = None,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get conversation history (placeholder).
        
        Args:
            conversation_id: Conversation ID
            user_id: Optional user ID
            project_id: Optional project ID
            
        Returns:
            Dict containing conversation history
        """
        try:
            logger.info(f"Getting conversation history for {conversation_id}")
            
            # Placeholder: In a real implementation, this would fetch from database
            return {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "project_id": project_id,
                "messages": [
                    {
                        "message_id": "msg_example",
                        "role": "user",
                        "content": "Example user message",
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    {
                        "message_id": "msg_example_2",
                        "role": "assistant",
                        "content": "Example AI response",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ],
                "status": "retrieved"
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            raise Exception(f"Failed to get conversation history: {str(e)}")
    
    async def validate_input(self, message: str) -> bool:
        """
        Validate input for conversation.
        
        Args:
            message: Input to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not message or not message.strip():
            return False
        
        if len(message.strip()) < 1:
            return False
            
        return True


# Global instance
conversation_service = ConversationService()