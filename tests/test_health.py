"""
Tests for health check endpoint.
"""

import pytest
from fastapi.testclient import TestClient
import json


def test_get_health_success(client):
    """Test successful health check."""
    response = client.get("/v1/health/")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response structure
    assert "status" in data
    assert "timestamp" in data
    assert "version" in data
    assert "environment" in data
    assert "services" in data
    assert "uptime_seconds" in data
    
    # Validate response values
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert isinstance(data["uptime_seconds"], int)
    assert data["uptime_seconds"] > 0
    
    # Validate services status
    services = data["services"]
    assert "database" in services
    assert "llm_providers" in services
    assert "file_storage" in services
    assert "cache" in services
    
    # All services should be healthy
    for service, status in services.items():
        assert status == "healthy"


def test_get_health_response_format(client):
    """Test health check response format."""
    response = client.get("/v1/health/")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    
    data = response.json()
    
    # Validate timestamp format (ISO 8601)
    timestamp = data["timestamp"]
    assert timestamp.endswith("Z")
    assert "T" in timestamp
    
    # Validate environment is string
    assert isinstance(data["environment"], str)


def test_ping_endpoint(client):
    """Test simple ping endpoint."""
    response = client.get("/v1/health/ping")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data == {"message": "pong"}


def test_health_endpoint_headers(client):
    """Test health endpoint returns correct headers."""
    response = client.get("/v1/health/")
    
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")


def test_health_endpoint_performance(client):
    """Test health endpoint response time is reasonable."""
    import time
    
    start_time = time.time()
    response = client.get("/v1/health/")
    end_time = time.time()
    
    assert response.status_code == 200
    
    # Response should be under 1 second
    response_time = end_time - start_time
    assert response_time < 1.0


def test_health_endpoint_multiple_calls(client):
    """Test health endpoint consistency across multiple calls."""
    responses = []
    
    for _ in range(3):
        response = client.get("/v1/health/")
        assert response.status_code == 200
        responses.append(response.json())
    
    # All responses should have consistent structure
    for data in responses:
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
        assert "services" in data


def test_health_endpoint_concurrent_requests(client):
    """Test health endpoint handles concurrent requests."""
    import concurrent.futures
    import threading
    
    def make_request():
        return client.get("/v1/health/")
    
    # Make 5 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request) for _ in range(5)]
        responses = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    # All responses should be successful
    for response in responses:
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"