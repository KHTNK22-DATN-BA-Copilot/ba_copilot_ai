"""
Tests for diagram endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_get_diagram_success(client, mock_diagram_id):
    """Test successful diagram retrieval."""
    response = client.get(f"/v1/diagrams/{mock_diagram_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response structure
    assert "diagram_id" in data
    assert "type" in data
    assert "title" in data
    assert "mermaid_code" in data
    assert "preview_url" in data
    assert "metadata" in data
    
    # Validate response values
    assert data["diagram_id"] == mock_diagram_id
    assert data["type"] == "sequence"
    assert data["title"] == "User Authentication Flow"
    assert isinstance(data["mermaid_code"], str)
    assert len(data["mermaid_code"]) > 0
    
    # Validate preview URL
    assert mock_diagram_id in data["preview_url"]
    assert "preview" in data["preview_url"]


def test_get_diagram_invalid_id_format(client):
    """Test diagram retrieval with invalid ID format."""
    invalid_id = "invalid_id_format"
    response = client.get(f"/v1/diagrams/{invalid_id}")
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid diagram ID format" in data["detail"]


def test_diagram_mermaid_code_validation(client, mock_diagram_id):
    """Test diagram Mermaid code validation."""
    response = client.get(f"/v1/diagrams/{mock_diagram_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    mermaid_code = data["mermaid_code"]
    
    # Check for valid Mermaid sequence diagram structure
    assert "sequenceDiagram" in mermaid_code
    assert "participant" in mermaid_code
    assert "User" in mermaid_code
    assert "Frontend" in mermaid_code
    assert "Backend" in mermaid_code
    assert "Database" in mermaid_code
    
    # Check for interactions
    assert "->>" in mermaid_code or "-->" in mermaid_code
    assert "Enter credentials" in mermaid_code
    assert "POST /auth/login" in mermaid_code


def test_diagram_metadata_validation(client, mock_diagram_id):
    """Test diagram metadata validation."""
    response = client.get(f"/v1/diagrams/{mock_diagram_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    metadata = data["metadata"]
    
    # Check required metadata fields
    required_fields = [
        "created_at", "updated_at", "status", "complexity",
        "actors_count", "interactions_count"
    ]
    
    for field in required_fields:
        assert field in metadata
        assert metadata[field] is not None
    
    # Validate specific metadata values
    assert metadata["status"] == "generated"
    assert metadata["complexity"] in ["low", "medium", "high"]
    assert isinstance(metadata["actors_count"], int)
    assert isinstance(metadata["interactions_count"], int)
    assert metadata["actors_count"] > 0
    assert metadata["interactions_count"] > 0


def test_export_diagram_svg(client, mock_diagram_id):
    """Test diagram export in SVG format."""
    response = client.get(
        f"/v1/diagrams/{mock_diagram_id}/export",
        params={"format": "svg", "quality": "medium", "theme": "default"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate export response structure
    assert "download_url" in data
    assert "expires_at" in data
    assert "file_size_bytes" in data
    assert "format" in data
    assert "quality" in data
    assert "theme" in data
    
    # Validate response values
    assert data["format"] == "svg"
    assert data["quality"] == "medium"
    assert data["theme"] == "default"
    assert isinstance(data["file_size_bytes"], int)
    assert data["file_size_bytes"] > 0
    assert mock_diagram_id in data["download_url"]
    assert data["download_url"].endswith(".svg")


def test_export_diagram_png(client, mock_diagram_id):
    """Test diagram export in PNG format."""
    response = client.get(
        f"/v1/diagrams/{mock_diagram_id}/export",
        params={"format": "png", "quality": "high", "theme": "dark"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["format"] == "png"
    assert data["quality"] == "high"
    assert data["theme"] == "dark"
    assert data["file_size_bytes"] > 0
    assert data["download_url"].endswith(".png")


def test_export_diagram_pdf(client, mock_diagram_id):
    """Test diagram export in PDF format."""
    response = client.get(
        f"/v1/diagrams/{mock_diagram_id}/export",
        params={"format": "pdf", "quality": "low", "theme": "forest"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["format"] == "pdf"
    assert data["quality"] == "low"
    assert data["theme"] == "forest"
    assert data["file_size_bytes"] > 0
    assert data["download_url"].endswith(".pdf")


def test_export_diagram_mermaid(client, mock_diagram_id):
    """Test diagram export in Mermaid format."""
    response = client.get(
        f"/v1/diagrams/{mock_diagram_id}/export",
        params={"format": "mermaid"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["format"] == "mermaid"
    assert data["file_size_bytes"] > 0
    assert data["download_url"].endswith(".mermaid")


def test_export_diagram_invalid_format(client, mock_diagram_id):
    """Test diagram export with invalid format."""
    response = client.get(
        f"/v1/diagrams/{mock_diagram_id}/export",
        params={"format": "invalid_format"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid format" in data["detail"]


def test_export_diagram_invalid_quality(client, mock_diagram_id):
    """Test diagram export with invalid quality."""
    response = client.get(
        f"/v1/diagrams/{mock_diagram_id}/export",
        params={"format": "png", "quality": "invalid_quality"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "Invalid quality" in data["detail"]


def test_export_diagram_invalid_theme(client, mock_diagram_id):
    """Test diagram export with invalid theme."""
    response = client.get(
        f"/v1/diagrams/{mock_diagram_id}/export",
        params={"format": "svg", "theme": "invalid_theme"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "Invalid theme" in data["detail"]


def test_list_diagrams_default(client):
    """Test listing diagrams with default parameters."""
    response = client.get("/v1/diagrams/")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response structure
    assert "diagrams" in data
    assert "total_count" in data
    assert "has_next" in data
    
    # Validate response values
    diagrams = data["diagrams"]
    assert isinstance(diagrams, list)
    assert len(diagrams) > 0
    assert isinstance(data["total_count"], int)
    assert isinstance(data["has_next"], bool)
    
    # Validate diagram structure
    for diagram in diagrams:
        assert "diagram_id" in diagram
        assert "type" in diagram
        assert "title" in diagram
        assert "created_at" in diagram
        assert "status" in diagram


def test_list_diagrams_with_type_filter(client):
    """Test listing diagrams with type filter."""
    response = client.get("/v1/diagrams/", params={"type": "sequence"})
    
    assert response.status_code == 200
    data = response.json()
    
    diagrams = data["diagrams"]
    for diagram in diagrams:
        assert diagram["type"] == "sequence"


def test_list_diagrams_with_pagination(client):
    """Test listing diagrams with pagination."""
    response = client.get("/v1/diagrams/", params={"limit": 2, "offset": 0})
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["diagrams"]) <= 2


def test_list_diagrams_with_search(client):
    """Test listing diagrams with search."""
    response = client.get("/v1/diagrams/", params={"search": "Authentication"})
    
    assert response.status_code == 200
    data = response.json()
    
    diagrams = data["diagrams"]
    for diagram in diagrams:
        assert "authentication" in diagram["title"].lower()


def test_list_diagrams_invalid_type(client):
    """Test listing diagrams with invalid type filter."""
    response = client.get("/v1/diagrams/", params={"type": "invalid_type"})
    
    assert response.status_code == 400
    data = response.json()
    assert "Invalid type" in data["detail"]


def test_list_diagrams_invalid_limit(client):
    """Test listing diagrams with invalid limit."""
    response = client.get("/v1/diagrams/", params={"limit": 0})
    
    assert response.status_code == 422  # Validation error


def test_list_diagrams_invalid_offset(client):
    """Test listing diagrams with invalid offset."""
    response = client.get("/v1/diagrams/", params={"offset": -1})
    
    assert response.status_code == 422  # Validation error


def test_diagram_response_headers(client, mock_diagram_id):
    """Test diagram endpoint returns correct headers."""
    response = client.get(f"/v1/diagrams/{mock_diagram_id}")
    
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")


def test_export_diagram_all_formats(client, mock_diagram_id):
    """Test diagram export with all supported formats."""
    formats = ["svg", "png", "pdf", "mermaid"]
    
    for fmt in formats:
        response = client.get(
            f"/v1/diagrams/{mock_diagram_id}/export",
            params={"format": fmt}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["format"] == fmt
        assert data["file_size_bytes"] > 0