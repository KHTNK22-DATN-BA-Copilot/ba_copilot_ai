"""
Tests for wireframe endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_get_wireframe_success(client, mock_wireframe_id):
    """Test successful wireframe retrieval."""
    response = client.get(f"/v1/wireframes/{mock_wireframe_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response structure
    assert "wireframe_id" in data
    assert "preview_url" in data
    assert "html_content" in data
    assert "css_styles" in data
    assert "components_identified" in data
    assert "metadata" in data
    
    # Validate response values
    assert data["wireframe_id"] == mock_wireframe_id
    assert isinstance(data["html_content"], str)
    assert isinstance(data["css_styles"], str)
    assert len(data["html_content"]) > 0
    assert len(data["css_styles"]) > 0
    
    # Validate preview URL
    assert mock_wireframe_id in data["preview_url"]
    assert "preview" in data["preview_url"]


def test_get_wireframe_invalid_id_format(client):
    """Test wireframe retrieval with invalid ID format."""
    invalid_id = "invalid_id_format"
    response = client.get(f"/v1/wireframes/{invalid_id}")
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid wireframe ID format" in data["detail"]


def test_wireframe_html_content_validation(client, mock_wireframe_id):
    """Test wireframe HTML content validation."""
    response = client.get(f"/v1/wireframes/{mock_wireframe_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    html_content = data["html_content"]
    
    # Check for valid HTML structure
    assert "<!DOCTYPE html>" in html_content
    assert "<html" in html_content
    assert "<head>" in html_content
    assert "<body>" in html_content
    assert "</html>" in html_content
    
    # Check for dashboard-specific elements
    assert "dashboard-container" in html_content
    assert "sidebar" in html_content
    assert "main-content" in html_content
    assert "analytics-section" in html_content


def test_wireframe_css_content_validation(client, mock_wireframe_id):
    """Test wireframe CSS content validation."""
    response = client.get(f"/v1/wireframes/{mock_wireframe_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    css_styles = data["css_styles"]
    
    # Check for CSS structure and classes
    assert ".dashboard-container" in css_styles
    assert ".sidebar" in css_styles
    assert ".main-content" in css_styles
    assert ".analytics-section" in css_styles
    
    # Check for responsive design
    assert "@media" in css_styles
    assert "768px" in css_styles  # Mobile breakpoint


def test_wireframe_components_validation(client, mock_wireframe_id):
    """Test wireframe components identification."""
    response = client.get(f"/v1/wireframes/{mock_wireframe_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    components = data["components_identified"]
    assert isinstance(components, list)
    assert len(components) > 0
    
    # Validate component structure
    for component in components:
        assert "type" in component
        assert "properties" in component
        assert isinstance(component["type"], str)
        assert isinstance(component["properties"], dict)
    
    # Check for expected component types
    component_types = [comp["type"] for comp in components]
    expected_types = ["navigation", "header", "chart", "stats_cards"]
    
    for expected_type in expected_types:
        assert expected_type in component_types


def test_wireframe_metadata_validation(client, mock_wireframe_id):
    """Test wireframe metadata validation."""
    response = client.get(f"/v1/wireframes/{mock_wireframe_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    metadata = data["metadata"]
    
    # Check required metadata fields
    required_fields = [
        "template_used", "responsive_breakpoints", "created_at",
        "updated_at", "status", "target_devices"
    ]
    
    for field in required_fields:
        assert field in metadata
        assert metadata[field] is not None
    
    # Validate specific metadata values
    assert metadata["template_used"] == "dashboard"
    assert metadata["status"] == "generated"
    assert isinstance(metadata["responsive_breakpoints"], list)
    assert isinstance(metadata["target_devices"], list)
    
    # Check responsive breakpoints
    breakpoints = metadata["responsive_breakpoints"]
    assert "768px" in breakpoints
    assert "1024px" in breakpoints
    assert "1200px" in breakpoints


def test_export_wireframe_html(client, mock_wireframe_id):
    """Test wireframe export in HTML format."""
    response = client.get(
        f"/v1/wireframes/{mock_wireframe_id}/export",
        params={"format": "html", "include_css": True, "responsive": True}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate export response structure
    assert "download_url" in data
    assert "expires_at" in data
    assert "file_size_bytes" in data
    assert "format" in data
    
    # Validate response values
    assert data["format"] == "html"
    assert isinstance(data["file_size_bytes"], int)
    assert data["file_size_bytes"] > 0
    assert mock_wireframe_id in data["download_url"]
    assert data["download_url"].endswith(".html")


def test_export_wireframe_zip(client, mock_wireframe_id):
    """Test wireframe export in ZIP format."""
    response = client.get(
        f"/v1/wireframes/{mock_wireframe_id}/export",
        params={"format": "zip", "include_css": True, "responsive": True}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["format"] == "zip"
    assert data["file_size_bytes"] > 0
    assert data["download_url"].endswith(".zip")


def test_export_wireframe_figma(client, mock_wireframe_id):
    """Test wireframe export in Figma format."""
    response = client.get(
        f"/v1/wireframes/{mock_wireframe_id}/export",
        params={"format": "figma", "include_css": False, "responsive": False}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["format"] == "figma"
    assert data["file_size_bytes"] > 0
    assert data["download_url"].endswith(".figma")


def test_export_wireframe_invalid_format(client, mock_wireframe_id):
    """Test wireframe export with invalid format."""
    response = client.get(
        f"/v1/wireframes/{mock_wireframe_id}/export",
        params={"format": "invalid_format"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid format" in data["detail"]


def test_export_wireframe_invalid_id(client):
    """Test wireframe export with invalid wireframe ID."""
    invalid_id = "invalid_id"
    response = client.get(
        f"/v1/wireframes/{invalid_id}/export",
        params={"format": "html"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "Invalid wireframe ID format" in data["detail"]


def test_wireframe_response_headers(client, mock_wireframe_id):
    """Test wireframe endpoint returns correct headers."""
    response = client.get(f"/v1/wireframes/{mock_wireframe_id}")
    
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")


def test_export_wireframe_query_parameters(client, mock_wireframe_id):
    """Test wireframe export with various query parameters."""
    # Test all supported formats
    formats = ["html", "zip", "figma"]
    
    for fmt in formats:
        response = client.get(
            f"/v1/wireframes/{mock_wireframe_id}/export",
            params={
                "format": fmt,
                "include_css": True,
                "responsive": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["format"] == fmt


def test_wireframe_html_structure_completeness(client, mock_wireframe_id):
    """Test wireframe HTML structure is complete and valid."""
    response = client.get(f"/v1/wireframes/{mock_wireframe_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    html_content = data["html_content"]
    
    # Check for essential HTML elements
    essential_elements = [
        "<meta charset=\"UTF-8\">",
        "<meta name=\"viewport\"",
        "<title>",
        "<nav",
        "<main",
        "<header",
        "<section"
    ]
    
    for element in essential_elements:
        assert element in html_content


def test_wireframe_css_responsive_design(client, mock_wireframe_id):
    """Test wireframe CSS includes responsive design elements."""
    response = client.get(f"/v1/wireframes/{mock_wireframe_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    css_styles = data["css_styles"]
    
    # Check for responsive design patterns
    responsive_patterns = [
        "@media (max-width: 768px)",
        "flex-direction: column",
        "grid-template-columns:",
        "width: 100%"
    ]
    
    for pattern in responsive_patterns:
        assert pattern in css_styles