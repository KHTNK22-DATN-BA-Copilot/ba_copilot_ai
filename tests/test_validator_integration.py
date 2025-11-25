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