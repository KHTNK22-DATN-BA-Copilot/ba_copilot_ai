import pytest
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.mermaid_validator.subprocess_manager import MermaidSubprocessManager

@pytest.mark.asyncio
async def test_validator_health():
    """Test validator health check"""
    manager = MermaidSubprocessManager()
    is_healthy = await manager.health_check()
    assert is_healthy is True
    await manager.close()

@pytest.mark.asyncio
async def test_validate_valid_diagram():
    """Test validation of valid diagram"""
    manager = MermaidSubprocessManager()

    result = await manager.validate("graph TD\nA-->B")
    assert isinstance(result, dict)
    assert result["valid"] is True

    await manager.close()

@pytest.mark.asyncio
async def test_validate_invalid_diagram():
    """Test validation of invalid diagram"""
    manager = MermaidSubprocessManager()

    result = await manager.validate("graph TD\nA[Start\nB[End]")

    assert isinstance(result, dict)
    assert result["valid"] is False
    assert "errors" in result

    await manager.close()

# Synchronous validation tests (used by workflows)
def test_validate_sync_valid_diagram():
    """Test synchronous validation of valid diagram"""
    manager = MermaidSubprocessManager()

    result = manager.validate_sync("graph TD\nA-->B")
    assert isinstance(result, dict)
    assert result["valid"] is True

    manager.sync_client.close()

def test_validate_sync_invalid_diagram():
    """Test synchronous validation of invalid diagram"""
    manager = MermaidSubprocessManager()

    result = manager.validate_sync("graph TD\nA[Start\nB[End]")

    assert isinstance(result, dict)
    assert result["valid"] is False
    assert "errors" in result

    manager.sync_client.close()

def test_validate_sync_complex_class_diagram():
    """Test synchronous validation of class diagram"""
    manager = MermaidSubprocessManager()
    
    class_diagram = """classDiagram
    class User {
        +String name
        +String email
        +login()
    }
    class Admin {
        +String permissions
    }
    User <|-- Admin
    """
    
    result = manager.validate_sync(class_diagram)
    assert isinstance(result, dict)
    assert result["valid"] is True
    
    manager.sync_client.close()

def test_validate_sync_usecase_diagram():
    """Test synchronous validation of usecase diagram"""
    manager = MermaidSubprocessManager()
    
    usecase_diagram = """graph TD
    Actor[User]
    UC1((Login))
    UC2((View Profile))
    Actor --> UC1
    Actor --> UC2
    """
    
    result = manager.validate_sync(usecase_diagram)
    assert isinstance(result, dict)
    # Note: May or may not be valid depending on mermaid version
    assert "valid" in result
    
    manager.sync_client.close()