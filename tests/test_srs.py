"""
Tests for SRS document endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import json


# Tests for POST /srs/generate endpoint

@pytest.mark.asyncio
async def test_generate_srs_document_success(client):
    """Test successful SRS document generation."""
    with patch('src.services.srs_service.get_llm_service') as mock_get_llm_service:
        # Mock the LLM service
        mock_llm_service = AsyncMock()
        mock_llm_service.generate_srs_document.return_value = {
            "title": "Math Learning Web Game",
            "version": "1.0",
            "author": "BA Copilot AI",
            "project_overview": "Interactive web-based math learning platform",
            "functional_requirements": ["User registration", "Interactive exercises"],
            "non_functional_requirements": ["High performance", "Security"]
        }
        mock_get_llm_service.return_value = mock_llm_service
        
        # Test data
        request_data = {
            "project_input": "Create a web-based math learning game for elementary school students with interactive exercises, progress tracking, and teacher dashboard."
        }
        
        # Make request
        response = client.post("/v1/srs/generate", json=request_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "document_id" in data
        assert "generated_at" in data
        assert "input_description" in data
        assert "document" in data
        assert "status" in data
        
        # Validate response values
        assert data["status"] == "completed"
        assert data["input_description"] == request_data["project_input"]
        assert isinstance(data["document"], dict)


@pytest.mark.asyncio 
async def test_generate_srs_document_invalid_input_empty(client):
    """Test SRS generation with empty input."""
    request_data = {"project_input": ""}
    
    response = client.post("/v1/srs/generate", json=request_data)
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_generate_srs_document_invalid_input_short(client):
    """Test SRS generation with too short input."""
    request_data = {"project_input": "short"}
    
    response = client.post("/v1/srs/generate", json=request_data)
    
    # Pydantic validation error (422) is expected for input too short
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_srs_document_service_error(client):
    """When LLM errors occur, the API should gracefully return a fallback document (HTTP 200)."""
    with patch('src.services.srs_service.get_llm_service') as mock_get_llm_service:
        # Mock LLM service to raise an error to force fallback path
        mock_llm_service = AsyncMock()
        mock_llm_service.generate_srs_document.side_effect = Exception("LLM service error")
        mock_get_llm_service.return_value = mock_llm_service

        request_data = {
            "project_input": "Valid input for testing error handling that is long enough"
        }

        response = client.post("/v1/srs/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert isinstance(data.get("document"), dict)


@pytest.mark.asyncio
async def test_generate_srs_document_validation_pydantic(client):
    """Test Pydantic validation for SRS generation request."""
    # Test missing required field
    response = client.post("/v1/srs/generate", json={})
    assert response.status_code == 422
    
    # Test field too long
    long_input = "a" * 10001
    request_data = {"project_input": long_input}
    response = client.post("/v1/srs/generate", json=request_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_srs_document_response_format(client):
    """Test SRS generation response format compliance."""
    with patch('src.services.srs_service.get_llm_service') as mock_get_llm_service:
        # Mock the LLM service
        mock_llm_service = AsyncMock()
        mock_llm_service.generate_srs_document.return_value = {
            "title": "Test Project",
            "version": "1.0",
            "author": "BA Copilot AI"
        }
        mock_get_llm_service.return_value = mock_llm_service
        
        request_data = {"project_input": "Test project description that is long enough"}
        response = client.post("/v1/srs/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check all required fields are present
        required_fields = ["document_id", "generated_at", "input_description", "document", "status"]
        for field in required_fields:
            assert field in data
            
        # Check data types
        assert isinstance(data["document_id"], str)
        assert isinstance(data["document"], dict)
        assert data["status"] == "completed"


# Tests for existing GET endpoints


def test_get_srs_document_success(client, mock_document_id):
    """Test successful SRS document retrieval."""
    response = client.get(f"/v1/srs/{mock_document_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response structure
    assert "document_id" in data
    assert "project_name" in data
    assert "content" in data
    assert "metadata" in data
    
    # Validate response values
    assert data["document_id"] == mock_document_id
    assert data["project_name"] == "E-commerce Platform"
    assert isinstance(data["content"], str)
    assert len(data["content"]) > 0
    
    # Validate metadata structure
    metadata = data["metadata"]
    assert "created_at" in metadata
    assert "updated_at" in metadata
    assert "template_used" in metadata
    assert "status" in metadata
    assert "word_count" in metadata
    assert "sections" in metadata
    
    assert metadata["status"] == "generated"
    assert metadata["template_used"] == "standard"


def test_get_srs_document_invalid_id_format(client):
    """Test SRS document retrieval with invalid ID format."""
    invalid_id = "invalid_id_format"
    response = client.get(f"/v1/srs/{invalid_id}")
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid document ID format" in data["detail"]


def test_get_srs_document_content_validation(client, mock_document_id):
    """Test SRS document content validation."""
    response = client.get(f"/v1/srs/{mock_document_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    content = data["content"]
    
    # Check for standard SRS sections
    assert "# Software Requirements Specification" in content
    assert "## 1. Introduction" in content
    assert "## 2. Overall Description" in content
    assert "## 3. System Requirements" in content
    assert "### 3.1 Functional Requirements" in content
    assert "### 3.2 Non-Functional Requirements" in content


def test_export_srs_document_markdown(client, mock_document_id):
    """Test SRS document export in Markdown format."""
    response = client.get(
        f"/v1/srs/{mock_document_id}/export",
        params={"format": "md"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate export response structure
    assert "download_url" in data
    assert "expires_at" in data
    assert "file_size_bytes" in data
    assert "format" in data
    
    # Validate response values
    assert data["format"] == "md"
    assert isinstance(data["file_size_bytes"], int)
    assert data["file_size_bytes"] > 0
    assert mock_document_id in data["download_url"]
    assert data["download_url"].endswith(".md")


def test_export_srs_document_pdf(client, mock_document_id):
    """Test SRS document export in PDF format."""
    response = client.get(
        f"/v1/srs/{mock_document_id}/export",
        params={"format": "pdf", "include_metadata": True, "include_diagrams": True}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["format"] == "pdf"
    assert data["file_size_bytes"] > 0
    assert data["download_url"].endswith(".pdf")


def test_export_srs_document_html(client, mock_document_id):
    """Test SRS document export in HTML format."""
    response = client.get(
        f"/v1/srs/{mock_document_id}/export",
        params={"format": "html", "include_metadata": False, "include_diagrams": False}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["format"] == "html"
    assert data["file_size_bytes"] > 0
    assert data["download_url"].endswith(".html")


def test_export_srs_document_invalid_format(client, mock_document_id):
    """Test SRS document export with invalid format."""
    response = client.get(
        f"/v1/srs/{mock_document_id}/export",
        params={"format": "invalid_format"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid format" in data["detail"]


def test_export_srs_document_invalid_id(client):
    """Test SRS document export with invalid document ID."""
    invalid_id = "invalid_id"
    response = client.get(
        f"/v1/srs/{invalid_id}/export",
        params={"format": "pdf"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "Invalid document ID format" in data["detail"]


def test_srs_document_response_headers(client, mock_document_id):
    """Test SRS document endpoint returns correct headers."""
    response = client.get(f"/v1/srs/{mock_document_id}")
    
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")


def test_export_srs_query_parameters(client, mock_document_id):
    """Test SRS export with various query parameters."""
    # Test all supported formats
    formats = ["md", "pdf", "html"]
    
    for fmt in formats:
        response = client.get(
            f"/v1/srs/{mock_document_id}/export",
            params={
                "format": fmt,
                "include_metadata": True,
                "include_diagrams": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["format"] == fmt


def test_srs_metadata_completeness(client, mock_document_id):
    """Test SRS document metadata completeness."""
    response = client.get(f"/v1/srs/{mock_document_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    metadata = data["metadata"]
    
    # Check all expected metadata fields
    required_fields = [
        "created_at", "updated_at", "template_used", 
        "status", "word_count", "sections"
    ]
    
    for field in required_fields:
        assert field in metadata
        assert metadata[field] is not None
    
    # Validate data types
    assert isinstance(metadata["word_count"], int)
    assert isinstance(metadata["sections"], int)
    assert metadata["word_count"] > 0
    assert metadata["sections"] > 0