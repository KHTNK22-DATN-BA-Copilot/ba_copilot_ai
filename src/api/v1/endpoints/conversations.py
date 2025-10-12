"""
Conversation endpoints.
"""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid
import logging

from services.conversation_service import conversation_service

logger = logging.getLogger(__name__)
router = APIRouter()


class MessageSendRequest(BaseModel):
    """Message send request model."""
    message: str
    conversation_id: Optional[str] = None
    project_id: Optional[int] = None


class MessageSendResponse(BaseModel):
    """Message send response model."""
    message_id: str
    conversation_id: str
    user_id: Optional[str]
    project_id: Optional[int]
    generated_at: str
    user_message: str
    ai_response: Dict[str, Any]
    status: str


class MessageModel(BaseModel):
    """Message model."""
    message_id: str
    role: str
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

class ConversationResponse(BaseModel):
    """Conversation response model."""
    conversation_id: str
    title: str
    messages: List[MessageModel]
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str

class ConversationListResponse(BaseModel):
    """Conversation list response model."""
    conversations: List[Dict[str, Any]]
    total_count: int
    has_next: bool


@router.post("/send", response_model=MessageSendResponse)
async def send_message(request: MessageSendRequest):
    """
    Send a message and get AI response.
    
    Args:
        request: Message send request containing the message content
    
    Returns:
        AI response with conversation metadata
    
    Raises:
        HTTPException: If processing fails or input is invalid
    """
    try:
        logger.info("Received conversation message")
        
        # Validate input
        if not await conversation_service.validate_input(request.message):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input: Message cannot be empty"
            )
        
        # Process message
        result = await conversation_service.send_message(
            message=request.message,
            conversation_id=request.conversation_id,
            user_id=None,  # TODO: Extract from JWT token when auth is implemented
            project_id=request.project_id
        )
        
        logger.info(f"Successfully processed message: {result['message_id']}")
        return MessageSendResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing conversation message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    """
    Retrieve conversation history.
    
    Args:
        conversation_id: The unique identifier for the conversation
    
    Returns:
        Conversation with complete message history and metadata
    """
    if not conversation_id.startswith("conv_"):
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")
    
    # Mock conversation data
    mock_messages = [
        MessageModel(
            message_id="msg_001",
            role="user",
            content="I need help creating an SRS document for my e-commerce project. Can you help me get started?",
            timestamp="2025-09-20T14:30:00Z",
            metadata={"word_count": 18}
        ),
        MessageModel(
            message_id="msg_002",
            role="assistant",
            content="I'd be happy to help you create an SRS document for your e-commerce project! To get started, I'll need some information about your project. Let me ask you a few questions:\n\n1. What is the main purpose of your e-commerce platform?\n2. Who is your target audience?\n3. What key features do you want to include?\n4. Are there any specific technical requirements or constraints?\n\nOnce I have these details, I can help you structure a comprehensive Software Requirements Specification document.",
            timestamp="2025-09-20T14:30:15Z",
            metadata={"word_count": 87, "response_time_ms": 1250}
        ),
        MessageModel(
            message_id="msg_003",
            role="user",
            content="It's a B2C platform for selling electronics. Target audience is tech-savvy consumers aged 25-45. Key features: product catalog, user accounts, shopping cart, payment gateway integration, order tracking, and admin dashboard.",
            timestamp="2025-09-20T14:32:30Z",
            metadata={"word_count": 35}
        ),
        MessageModel(
            message_id="msg_004",
            role="assistant",
            content="Perfect! Based on your requirements, I'll help you create a comprehensive SRS document. Here's what I'll include:\n\n**1. Introduction & Scope**\n- Purpose: B2C electronics e-commerce platform\n- Target users: Tech-savvy consumers (25-45 years)\n\n**2. Functional Requirements**\n- User Management (registration, authentication, profiles)\n- Product Catalog (browsing, searching, filtering)\n- Shopping Cart & Checkout\n- Payment Processing\n- Order Management & Tracking\n- Administrative Dashboard\n\n**3. Non-Functional Requirements**\n- Performance, security, scalability considerations\n\n**4. System Architecture**\n- High-level system design\n- Technology stack recommendations\n\nWould you like me to generate the complete SRS document with these sections, or would you like to add any specific technical constraints or additional features first?",
            timestamp="2025-09-20T14:32:45Z",
            metadata={"word_count": 142, "response_time_ms": 1800}
        )
    ]
    
    return ConversationResponse(
        conversation_id=conversation_id,
        title="E-commerce SRS Development Discussion",
        messages=mock_messages,
        metadata={
            "project_type": "e-commerce",
            "domain": "electronics",
            "llm_provider": "openai",
            "total_messages": len(mock_messages),
            "user_messages": 2,
            "assistant_messages": 2,
            "average_response_time_ms": 1525,
            "conversation_status": "active",
            "last_activity": "2025-09-20T14:32:45Z"
        },
        created_at="2025-09-20T14:30:00Z",
        updated_at="2025-09-20T14:32:45Z"
    )

@router.get("/", response_model=ConversationListResponse)
async def list_conversations(
    limit: int = Query(20, ge=1, le=100, description="Maximum conversations to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    search: Optional[str] = Query(None, description="Search in conversation titles"),
    status: Optional[str] = Query(None, description="Filter by conversation status")
):
    """
    List user's conversations.
    
    Args:
        limit: Maximum conversations to return (1-100)
        offset: Pagination offset
        search: Search term for conversation titles
        status: Filter by conversation status (active, archived, completed)
    
    Returns:
        List of conversations with pagination info
    """
    if status and status not in ["active", "archived", "completed"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid status. Supported: active, archived, completed"
        )
    
    # Mock conversation data
    mock_conversations = [
        {
            "conversation_id": "conv_550e8400-001",
            "title": "E-commerce SRS Development Discussion",
            "created_at": "2025-09-20T14:30:00Z",
            "updated_at": "2025-09-20T14:32:45Z",
            "message_count": 4,
            "status": "active",
            "preview": "I need help creating an SRS document for my e-commerce project..."
        },
        {
            "conversation_id": "conv_550e8400-002",
            "title": "Mobile App Wireframe Planning",
            "created_at": "2025-09-19T10:15:00Z",
            "updated_at": "2025-09-19T11:30:00Z",
            "message_count": 8,
            "status": "completed",
            "preview": "Can you help me design wireframes for a mobile banking app?"
        },
        {
            "conversation_id": "conv_550e8400-003",
            "title": "System Architecture Review",
            "created_at": "2025-09-18T16:45:00Z",
            "updated_at": "2025-09-18T17:20:00Z",
            "message_count": 6,
            "status": "active",
            "preview": "I need to review the architecture for our microservices platform..."
        },
        {
            "conversation_id": "conv_550e8400-004",
            "title": "API Documentation Discussion",
            "created_at": "2025-09-17T09:20:00Z",
            "updated_at": "2025-09-17T10:45:00Z",
            "message_count": 12,
            "status": "archived",
            "preview": "Let's discuss the best practices for API documentation..."
        }
    ]
    
    # Apply filters
    filtered_conversations = mock_conversations
    if status:
        filtered_conversations = [c for c in filtered_conversations if c["status"] == status]
    
    if search:
        filtered_conversations = [
            c for c in filtered_conversations 
            if search.lower() in c["title"].lower() or search.lower() in c["preview"].lower()
        ]
    
    # Apply pagination
    total_count = len(filtered_conversations)
    paginated_conversations = filtered_conversations[offset:offset + limit]
    has_next = offset + limit < total_count
    
    return ConversationListResponse(
        conversations=paginated_conversations,
        total_count=total_count,
        has_next=has_next
    )