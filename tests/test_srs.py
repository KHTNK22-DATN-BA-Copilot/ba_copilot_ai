"""
Tests for SRS document endpoints.
"""

import pytest
from fastapi.testclient import TestClient


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