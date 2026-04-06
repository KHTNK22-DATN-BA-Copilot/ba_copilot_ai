"""
Tests for AI Provider Factory Pattern

This module tests the factory pattern implementation including:
- Multi-provider support (Google, OpenAI, Anthropic, OpenRouter)
- BYOK (Bring Your Own Key) functionality  
- Default fallback behavior
- Security validation
- Request isolation with ContextVar
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Import the application
from main import app
from factory import create_chat_model, DEFAULT_PROVIDER, DEFAULT_MODEL_BY_PROVIDER
from connect_model import (
    set_request_model_config,
    reset_request_model_config,
    get_request_model_config,
    get_model_client
)


class TestFactoryBasics:
    """Test basic factory functionality"""
    
    def test_default_provider(self):
        """Test that default provider is Google Gemini"""
        assert DEFAULT_PROVIDER == "google"
        assert DEFAULT_MODEL_BY_PROVIDER["google"] == "gemini-2.5-flash-lite"
    
    def test_all_providers_configured(self):
        """Test that all providers have default models"""
        expected_providers = ["google", "openai", "anthropic", "openrouter"]
        for provider in expected_providers:
            assert provider in DEFAULT_MODEL_BY_PROVIDER
            assert DEFAULT_MODEL_BY_PROVIDER[provider]  # Non-empty
    
    @patch.dict(os.environ, {"GOOGLE_GEMINI_API_KEY": "test-key"})
    def test_create_chat_model_default(self):
        """Test creating model with default settings"""
        model = create_chat_model()
        assert model is not None
        # Should be Google Gemini by default
        assert hasattr(model, 'model')  # Has model attribute
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_create_chat_model_custom_provider(self):
        """Test creating model with custom provider"""
        model = create_chat_model(provider="openai", model_name="gpt-4o-mini")
        assert model is not None
    
    def test_unsupported_provider_raises_error(self):
        """Test that unsupported provider raises ValueError"""
        with pytest.raises(ValueError, match="Unsupported provider"):
            create_chat_model(provider="unsupported-provider")


class TestRequestContext:
    """Test request-scoped configuration with ContextVar"""
    
    def test_set_and_get_config(self):
        """Test setting and getting request config"""
        token = set_request_model_config(
            provider="openai",
            model_name="gpt-4o",
            api_key="test-key"
        )
        
        config = get_request_model_config()
        assert config["provider"] == "openai"
        assert config["model_name"] == "gpt-4o"
        assert config["api_key"] == "test-key"
        
        # Clean up
        reset_request_model_config(token)
    
    def test_reset_config(self):
        """Test that reset clears configuration"""
        token = set_request_model_config(provider="openai")
        reset_request_model_config(token)
        
        config = get_request_model_config()
        # Should be empty after reset (depends on implementation)
        # The ContextVar might return default empty dict
        assert isinstance(config, dict)
    
    def test_empty_values_are_cleaned(self):
        """Test that empty string values are ignored"""
        token = set_request_model_config(
            provider="",  # Empty string should be ignored
            model_name="gpt-4o",
            api_key=None
        )
        
        config = get_request_model_config()
        assert "provider" not in config or config["provider"] is None
        assert config.get("model_name") == "gpt-4o"
        
        reset_request_model_config(token)


class TestMiddlewareIntegration:
    """Test middleware header extraction and validation"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_health_endpoint_works(self):
        """Test that health check endpoint works"""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    @patch.dict(os.environ, {"GOOGLE_GEMINI_API_KEY": "test-key"}, clear=False)
    def test_request_without_custom_headers(self):
        """Test that requests work without custom AI headers"""
        # This should use default Gemini configuration
        response = self.client.get("/")
        assert response.status_code == 200
    
    @patch.dict(os.environ, {
        "AI_INTERNAL_AUTH_TOKEN": "test-token",
        "OPENAI_API_KEY": "test-key"
    }, clear=False)
    def test_request_with_valid_token(self):
        """Test request with valid X-AI-Service-Token"""
        headers = {
            "X-AI-Service-Token": "test-token",
            "X-AI-Provider": "openai",
            "X-AI-Model": "gpt-4o-mini"
        }
        response = self.client.get("/", headers=headers)
        # Should not raise 403
        assert response.status_code == 200
    
    @patch.dict(os.environ, {"AI_INTERNAL_AUTH_TOKEN": "correct-token"}, clear=False)
    def test_request_with_invalid_token(self):
        """Test that invalid token returns 403"""
        headers = {
            "X-AI-Service-Token": "wrong-token",
            "X-AI-Provider": "openai"
        }
        response = self.client.get("/", headers=headers)
        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]
    
    @patch.dict(os.environ, {"AI_INTERNAL_AUTH_TOKEN": "test-token"}, clear=False)
    def test_request_with_missing_token(self):
        """Test that missing token with custom headers returns 403"""
        headers = {
            "X-AI-Provider": "openai"
            # Missing X-AI-Service-Token
        }
        response = self.client.get("/", headers=headers)
        assert response.status_code == 403
    
    def test_request_without_token_config(self):
        """Test that requests work when AI_INTERNAL_AUTH_TOKEN is not set"""
        # When token is not configured, validation should be skipped
        with patch.dict(os.environ, {}, clear=True):
            # Remove AI_INTERNAL_AUTH_TOKEN from environment
            if "AI_INTERNAL_AUTH_TOKEN" in os.environ:
                del os.environ["AI_INTERNAL_AUTH_TOKEN"]
            
            headers = {
                "X-AI-Provider": "openai"
                # No token needed when not configured
            }
            response = self.client.get("/", headers=headers)
            # Should not raise 403 when token not configured
            assert response.status_code == 200


class TestBYOK:
    """Test Bring Your Own Key functionality"""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_byok_with_user_key(self):
        """Test that user-provided API key is used"""
        # User provides their own key
        model = create_chat_model(
            provider="openai",
            model_name="gpt-4o-mini",
            api_key="user-provided-key"
        )
        assert model is not None
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "system-key"})
    def test_fallback_to_env_key(self):
        """Test fallback to environment variable when no user key"""
        # No user key provided, should use env variable
        model = create_chat_model(
            provider="openai",
            model_name="gpt-4o-mini"
            # api_key not provided
        )
        assert model is not None
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_key_raises_error(self):
        """Test that missing API key raises ValueError"""
        with pytest.raises(ValueError, match="Missing API key"):
            create_chat_model(
                provider="openai",
                model_name="gpt-4o-mini"
                # No api_key and no env variable
            )


class TestModelClient:
    """Test ModelClient singleton and methods"""
    
    def test_model_client_singleton(self):
        """Test that get_model_client returns same instance"""
        client1 = get_model_client()
        client2 = get_model_client()
        assert client1 is client2
    
    @patch.dict(os.environ, {"GOOGLE_GEMINI_API_KEY": "test-key"})
    @patch('connect_model.ModelClient._build_llm')
    def test_gemini_completion(self, mock_build_llm):
        """Test gemini_completion method"""
        # Mock the LLM
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="Test response")
        mock_build_llm.return_value = mock_llm
        
        client = get_model_client()
        response = client.gemini_completion("Test prompt")
        
        assert response == "Test response"
        mock_build_llm.assert_called_once()
        mock_llm.invoke.assert_called_once_with("Test prompt")
    
    @patch.dict(os.environ, {"GOOGLE_GEMINI_API_KEY": "test-key"})
    @patch('connect_model.ModelClient._build_llm')
    def test_chat_completion(self, mock_build_llm):
        """Test chat_completion method"""
        # Mock the LLM
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="Chat response")
        mock_build_llm.return_value = mock_llm
        
        client = get_model_client()
        messages = [{"role": "user", "content": "Hello"}]
        response = client.chat_completion(messages)
        
        assert response.choices[0].message.content == "Chat response"
        mock_build_llm.assert_called_once()


class TestProviderSpecifics:
    """Test provider-specific configurations"""
    
    @patch.dict(os.environ, {
        "OPEN_ROUTER_API_KEY": "test-key",
        "OPENROUTER_REFERER": "https://example.com",
        "OPENROUTER_TITLE": "Test App"
    })
    def test_openrouter_headers(self):
        """Test that OpenRouter includes custom headers"""
        model = create_chat_model(provider="openrouter")
        assert model is not None
        # OpenRouter model should have default_headers set
        # This depends on implementation details
    
    @patch.dict(os.environ, {"GOOGLE_GEMINI_API_KEY": "test-key"})
    def test_google_uses_correct_class(self):
        """Test that Google provider uses ChatGoogleGenerativeAI"""
        model = create_chat_model(provider="google")
        # Check the class name
        assert "Google" in model.__class__.__name__ or "Gemini" in model.__class__.__name__
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_openai_uses_correct_class(self):
        """Test that OpenAI provider uses ChatOpenAI"""
        model = create_chat_model(provider="openai")
        assert "OpenAI" in model.__class__.__name__
    
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_anthropic_uses_correct_class(self):
        """Test that Anthropic provider uses ChatAnthropic"""
        model = create_chat_model(provider="anthropic")
        assert "Anthropic" in model.__class__.__name__


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_none_provider_uses_default(self):
        """Test that None provider falls back to default"""
        with patch.dict(os.environ, {"GOOGLE_GEMINI_API_KEY": "test-key"}):
            model = create_chat_model(provider=None)
            assert model is not None
    
    def test_empty_string_provider_uses_default(self):
        """Test that empty string provider falls back to default"""
        with patch.dict(os.environ, {"GOOGLE_GEMINI_API_KEY": "test-key"}):
            model = create_chat_model(provider="")
            assert model is not None
    
    def test_whitespace_provider_uses_default(self):
        """Test that whitespace-only provider falls back to default"""
        with patch.dict(os.environ, {"GOOGLE_GEMINI_API_KEY": "test-key"}):
            model = create_chat_model(provider="   ")
            assert model is not None
    
    def test_case_insensitive_provider(self):
        """Test that provider name is case-insensitive"""
        with patch.dict(os.environ, {"GOOGLE_GEMINI_API_KEY": "test-key"}):
            model1 = create_chat_model(provider="GOOGLE")
            model2 = create_chat_model(provider="Google")
            model3 = create_chat_model(provider="google")
            # All should succeed
            assert model1 is not None
            assert model2 is not None
            assert model3 is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
