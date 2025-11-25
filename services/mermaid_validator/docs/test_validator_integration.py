import pytest
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
    assert result is True

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