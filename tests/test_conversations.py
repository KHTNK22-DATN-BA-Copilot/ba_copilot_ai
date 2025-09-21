"""
Tests for conversation endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_get_conversation_success(client, mock_conversation_id):
    """Test successful conversation retrieval."""
    response = client.get(f"/v1/conversations/{mock_conversation_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response structure
    assert "conversation_id" in data
    assert "title" in data
    assert "messages" in data
    assert "metadata" in data
    assert "created_at" in data
    assert "updated_at" in data
    
    # Validate response values
    assert data["conversation_id"] == mock_conversation_id
    assert data["title"] == "E-commerce SRS Development Discussion"
    assert isinstance(data["messages"], list)
    assert len(data["messages"]) > 0


def test_get_conversation_invalid_id_format(client):
    """Test conversation retrieval with invalid ID format."""
    invalid_id = "invalid_id_format"
    response = client.get(f"/v1/conversations/{invalid_id}")
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid conversation ID format" in data["detail"]


def test_conversation_messages_validation(client, mock_conversation_id):
    """Test conversation messages structure validation."""
    response = client.get(f"/v1/conversations/{mock_conversation_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    messages = data["messages"]
    assert isinstance(messages, list)
    assert len(messages) > 0
    
    # Validate message structure
    for message in messages:
        assert "message_id" in message
        assert "role" in message
        assert "content" in message
        assert "timestamp" in message
        
        # Validate role values
        assert message["role"] in ["user", "assistant"]
        
        # Validate content
        assert isinstance(message["content"], str)
        assert len(message["content"]) > 0
        
        # Validate metadata (optional)
        if "metadata" in message:
            assert isinstance(message["metadata"], dict)


def test_conversation_messages_alternating_roles(client, mock_conversation_id):
    """Test conversation messages have alternating user/assistant roles."""
    response = client.get(f"/v1/conversations/{mock_conversation_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    messages = data["messages"]
    
    # Check that conversation starts with user message
    assert messages[0]["role"] == "user"
    
    # Check alternating pattern
    for i in range(1, len(messages)):
        if messages[i-1]["role"] == "user":
            assert messages[i]["role"] == "assistant"
        else:
            assert messages[i]["role"] == "user"


def test_conversation_metadata_validation(client, mock_conversation_id):
    """Test conversation metadata validation."""
    response = client.get(f"/v1/conversations/{mock_conversation_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    metadata = data["metadata"]
    
    # Check required metadata fields
    required_fields = [
        "project_type", "domain", "llm_provider", "total_messages",
        "user_messages", "assistant_messages", "average_response_time_ms",
        "conversation_status", "last_activity"
    ]
    
    for field in required_fields:
        assert field in metadata
        assert metadata[field] is not None
    
    # Validate specific metadata values
    assert metadata["project_type"] == "e-commerce"
    assert metadata["domain"] == "electronics"
    assert metadata["llm_provider"] == "openai"
    assert metadata["conversation_status"] == "active"
    
    # Validate numeric fields
    assert isinstance(metadata["total_messages"], int)
    assert isinstance(metadata["user_messages"], int)
    assert isinstance(metadata["assistant_messages"], int)
    assert isinstance(metadata["average_response_time_ms"], int)
    
    assert metadata["total_messages"] > 0
    assert metadata["user_messages"] > 0
    assert metadata["assistant_messages"] > 0
    assert metadata["average_response_time_ms"] > 0


def test_conversation_message_count_consistency(client, mock_conversation_id):
    """Test conversation message count consistency."""
    response = client.get(f"/v1/conversations/{mock_conversation_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    messages = data["messages"]
    metadata = data["metadata"]
    
    # Count actual messages by role
    user_messages = len([m for m in messages if m["role"] == "user"])
    assistant_messages = len([m for m in messages if m["role"] == "assistant"])
    total_messages = len(messages)
    
    # Validate counts match metadata
    assert metadata["total_messages"] == total_messages
    assert metadata["user_messages"] == user_messages
    assert metadata["assistant_messages"] == assistant_messages


def test_list_conversations_default(client):
    """Test listing conversations with default parameters."""
    response = client.get("/v1/conversations/")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response structure
    assert "conversations" in data
    assert "total_count" in data
    assert "has_next" in data
    
    # Validate response values
    conversations = data["conversations"]
    assert isinstance(conversations, list)
    assert len(conversations) > 0
    assert isinstance(data["total_count"], int)
    assert isinstance(data["has_next"], bool)
    
    # Validate conversation structure
    for conversation in conversations:
        assert "conversation_id" in conversation
        assert "title" in conversation
        assert "created_at" in conversation
        assert "updated_at" in conversation
        assert "message_count" in conversation
        assert "status" in conversation
        assert "preview" in conversation


def test_list_conversations_with_status_filter(client):
    """Test listing conversations with status filter."""
    response = client.get("/v1/conversations/", params={"status": "active"})
    
    assert response.status_code == 200
    data = response.json()
    
    conversations = data["conversations"]
    for conversation in conversations:
        assert conversation["status"] == "active"


def test_list_conversations_with_pagination(client):
    """Test listing conversations with pagination."""
    response = client.get("/v1/conversations/", params={"limit": 2, "offset": 0})
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["conversations"]) <= 2


def test_list_conversations_with_search(client):
    """Test listing conversations with search."""
    response = client.get("/v1/conversations/", params={"search": "SRS"})
    
    assert response.status_code == 200
    data = response.json()
    
    conversations = data["conversations"]
    for conversation in conversations:
        search_text = (conversation["title"] + " " + conversation["preview"]).lower()
        assert "srs" in search_text


def test_list_conversations_invalid_status(client):
    """Test listing conversations with invalid status filter."""
    response = client.get("/v1/conversations/", params={"status": "invalid_status"})
    
    assert response.status_code == 400
    data = response.json()
    assert "Invalid status" in data["detail"]


def test_list_conversations_invalid_limit(client):
    """Test listing conversations with invalid limit."""
    response = client.get("/v1/conversations/", params={"limit": 0})
    
    assert response.status_code == 422  # Validation error


def test_list_conversations_invalid_offset(client):
    """Test listing conversations with invalid offset."""
    response = client.get("/v1/conversations/", params={"offset": -1})
    
    assert response.status_code == 422  # Validation error


def test_conversation_response_headers(client, mock_conversation_id):
    """Test conversation endpoint returns correct headers."""
    response = client.get(f"/v1/conversations/{mock_conversation_id}")
    
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")


def test_conversation_timestamp_format(client, mock_conversation_id):
    """Test conversation timestamps are in ISO 8601 format."""
    response = client.get(f"/v1/conversations/{mock_conversation_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check conversation timestamps
    assert data["created_at"].endswith("Z")
    assert data["updated_at"].endswith("Z")
    assert "T" in data["created_at"]
    assert "T" in data["updated_at"]
    
    # Check message timestamps
    for message in data["messages"]:
        timestamp = message["timestamp"]
        assert timestamp.endswith("Z")
        assert "T" in timestamp


def test_conversation_preview_content(client):
    """Test conversation list previews contain relevant content."""
    response = client.get("/v1/conversations/")
    
    assert response.status_code == 200
    data = response.json()
    
    conversations = data["conversations"]
    for conversation in conversations:
        preview = conversation["preview"]
        assert isinstance(preview, str)
        assert len(preview) > 0
        assert len(preview) <= 200  # Preview should be truncated


def test_conversation_status_values(client):
    """Test conversation status values are valid."""
    response = client.get("/v1/conversations/")
    
    assert response.status_code == 200
    data = response.json()
    
    valid_statuses = ["active", "archived", "completed"]
    conversations = data["conversations"]
    
    for conversation in conversations:
        assert conversation["status"] in valid_statuses


def test_conversation_message_metadata(client, mock_conversation_id):
    """Test conversation message metadata structure."""
    response = client.get(f"/v1/conversations/{mock_conversation_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    messages = data["messages"]
    
    for message in messages:
        if "metadata" in message:
            metadata = message["metadata"]
            
            # Check common metadata fields
            if "word_count" in metadata:
                assert isinstance(metadata["word_count"], int)
                assert metadata["word_count"] > 0
            
            if "response_time_ms" in metadata:
                assert isinstance(metadata["response_time_ms"], int)
                assert metadata["response_time_ms"] > 0