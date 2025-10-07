"""
PyTest configuration and fixtures for BA Copilot AI Services tests.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.main import app

@pytest.fixture
def client():
    """Create FastAPI test client."""
    return TestClient(app)

@pytest.fixture
def mock_document_id():
    """Mock document ID for testing."""
    return "doc_550e8400-e29b-41d4-a716-446655440000"

@pytest.fixture
def mock_wireframe_id():
    """Mock wireframe ID for testing."""
    return "wf_550e8400-e29b-41d4-a716-446655440000"

@pytest.fixture
def mock_diagram_id():
    """Mock diagram ID for testing."""
    return "diag_550e8400-seq-001"

@pytest.fixture
def mock_conversation_id():
    """Mock conversation ID for testing."""
    return "conv_550e8400-001"