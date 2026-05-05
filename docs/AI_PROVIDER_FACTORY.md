# AI Provider Factory - Architecture & Usage Guide

## Overview

The BA Copilot AI service uses a **Factory Pattern** to support multiple AI providers with flexible configuration. This allows:

1. **Bring Your Own Key (BYOK)** - Users can supply their own API keys via request headers
2. **Multi-Provider Support** - Google Gemini, OpenAI, Anthropic, and OpenRouter
3. **Smart Fallback** - Automatically uses system-configured keys when user keys aren't provided
4. **Request Isolation** - Concurrent requests never leak credentials across users/tenants

---

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      HTTP Request                            │
│  Headers: X-AI-Provider, X-AI-Model, X-AI-API-Key          │
│           X-AI-Service-Token (required for custom headers)   │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   v
┌─────────────────────────────────────────────────────────────┐
│              main.py: Middleware Layer                       │
│  - Validates X-AI-Service-Token (security check)            │
│  - Extracts headers and sets request-scoped context         │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   v
┌─────────────────────────────────────────────────────────────┐
│         connect_model.py: Request Context Manager           │
│  - Uses ContextVar for thread-safe request isolation        │
│  - Provides get_model_client() for workflows                │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   v
┌─────────────────────────────────────────────────────────────┐
│          factory.py: Provider Factory (Core)                │
│  - create_chat_model(provider, model_name, api_key)        │
│  - Handles all provider-specific instantiation              │
│  - Falls back to environment variables if no key provided   │
└─────────────────────────────────────────────────────────────┘
```

### Key Files

| File | Purpose | Key Functions |
|------|---------|---------------|
| `factory.py` | Core factory for creating LangChain chat models | `create_chat_model()`, `_resolve_api_key()` |
| `connect_model.py` | Request-scoped configuration management | `set_request_model_config()`, `get_model_client()` |
| `main.py` | HTTP middleware for header extraction | `attach_model_config()`, `_validate_internal_model_header_access()` |

---

## Supported Providers

### 1. **Google Gemini** (Default)
- **Default Model:** `gemini-2.5-flash-lite`
- **Environment Variables:** `GOOGLE_GEMINI_API_KEY` or `GOOGLE_AI_API_KEY`
- **LangChain Class:** `ChatGoogleGenerativeAI`

### 2. **OpenAI**
- **Default Model:** `gpt-4o-mini`
- **Environment Variable:** `OPENAI_API_KEY`
- **LangChain Class:** `ChatOpenAI`

### 3. **Anthropic**
- **Default Model:** `claude-3-5-sonnet-latest`
- **Environment Variable:** `ANTHROPIC_API_KEY`
- **LangChain Class:** `ChatAnthropic`

### 4. **OpenRouter**
- **Default Model:** `anthropic/claude-3.5-sonnet`
- **Environment Variables:** 
  - `OPEN_ROUTER_API_KEY` or `OPENROUTER_API_KEY`
  - `OPENROUTER_BASE_URL` (optional, defaults to `https://openrouter.ai/api/v1`)
  - `OPENROUTER_REFERER` (optional, sent as `HTTP-Referer` header)
  - `OPENROUTER_TITLE` (optional, sent as `X-Title` header)
- **LangChain Class:** `ChatOpenAI` (with custom base_url)

---

## Usage Patterns

### Pattern 1: Default System Configuration (No Custom Headers)

**Request:**
```http
POST /api/generate-srs
Content-Type: application/json

{
  "message": "Create SRS for E-commerce Platform",
  "content_id": null,
  "storage_paths": []
}
```

**Behavior:**
- Uses default provider: `Google Gemini`
- Uses default model: `gemini-2.5-flash-lite`
- Uses API key from environment variable `GOOGLE_GEMINI_API_KEY`

---

### Pattern 2: Bring Your Own Key (BYOK)

**Request:**
```http
POST /api/generate-srs
Content-Type: application/json
X-AI-Service-Token: your-internal-token-here
X-AI-Provider: openai
X-AI-Model: gpt-4o
X-AI-API-Key: sk-user-supplied-key-here

{
  "message": "Create SRS for E-commerce Platform"
}
```

**Behavior:**
- Uses provider: `OpenAI`
- Uses model: `gpt-4o`
- Uses user-supplied API key: `sk-user-supplied-key-here`
- **Security:** Requires valid `X-AI-Service-Token` to prevent unauthorized BYOK usage

---

### Pattern 3: Custom Provider with System Key

**Request:**
```http
POST /api/generate-class-diagram
Content-Type: application/json
X-AI-Service-Token: your-internal-token-here
X-AI-Provider: anthropic
X-AI-Model: claude-3-5-sonnet-latest

{
  "message": "Generate class diagram for user management system"
}
```

**Behavior:**
- Uses provider: `Anthropic`
- Uses model: `claude-3-5-sonnet-latest`
- Falls back to environment variable `ANTHROPIC_API_KEY` (no user key provided)

---

## Security Model

### Authorization Token

When custom AI headers (`X-AI-Provider`, `X-AI-Model`, `X-AI-API-Key`) are present, the system requires a valid `X-AI-Service-Token`.

**Configuration:**
```bash
# .env
AI_INTERNAL_AUTH_TOKEN=your-secret-token-here
```

**Middleware Validation:**
```python
def _validate_internal_model_header_access(request: Request) -> None:
    """Allow BYOK/model headers only for trusted backend calls."""
    expected_token = os.getenv("AI_INTERNAL_AUTH_TOKEN")
    if not expected_token:
        return  # No validation if token not configured
    
    provided_token = request.headers.get("X-AI-Service-Token")
    if not provided_token or not hmac.compare_digest(provided_token, expected_token):
        raise HTTPException(status_code=403, detail="Forbidden: invalid X-AI-Service-Token")
```

**Why?**
- Prevents unauthorized users from using their own API keys through your service
- Restricts BYOK to trusted backend services only
- Optional: If `AI_INTERNAL_AUTH_TOKEN` is not set, no validation is performed

---

## Request Isolation (Thread Safety)

The system uses Python's `ContextVar` to ensure request-scoped isolation:

```python
from contextvars import ContextVar

_request_model_config: ContextVar[Dict[str, str]] = ContextVar("request_model_config", default={})

def set_request_model_config(provider, model_name, api_key):
    """Set configuration for current request only."""
    cfg = {"provider": provider, "model_name": model_name, "api_key": api_key}
    return _request_model_config.set(cfg)
```

**Benefits:**
- Concurrent requests don't interfere with each other
- No global state mutation
- Automatic cleanup after request completes
- Safe for multi-tenant environments

---

## Adding a New Provider

To add support for a new AI provider (e.g., Cohere):

### Step 1: Update `factory.py`

```python
# 1. Import the LangChain class
from langchain_cohere import ChatCohere

# 2. Add to default models
DEFAULT_MODEL_BY_PROVIDER = {
    # ... existing providers ...
    "cohere": "command-r-plus",
}

# 3. Add API key resolution
def _resolve_api_key(provider: str, user_api_key: Optional[str]) -> str:
    # ... existing code ...
    
    if provider == "cohere":
        key = _clean(os.getenv("COHERE_API_KEY"))
        if key:
            return key
        raise ValueError("Missing API key for Cohere provider. Set COHERE_API_KEY.")
    
    # ... rest of function ...

# 4. Add model creation logic
def create_chat_model(...) -> BaseChatModel:
    # ... existing code ...
    
    if resolved_provider == "cohere":
        return ChatCohere(
            model=resolved_model_name,
            cohere_api_key=resolved_api_key,
            **kwargs,
        )
    
    # ... rest of function ...
```

### Step 2: Update Environment Variables

```bash
# .env
COHERE_API_KEY=your-cohere-key-here
```

### Step 3: Test

```http
POST /api/generate-srs
Content-Type: application/json
X-AI-Service-Token: your-token
X-AI-Provider: cohere
X-AI-Model: command-r-plus

{
  "message": "Test Cohere integration"
}
```

---

## Testing

### Test Scenarios

1. **Default Provider (No Headers)**
   ```bash
   curl -X POST http://localhost:8000/api/generate-srs \
     -H "Content-Type: application/json" \
     -d '{"message": "Test default Gemini"}'
   ```

2. **BYOK with Valid Token**
   ```bash
   curl -X POST http://localhost:8000/api/generate-srs \
     -H "Content-Type: application/json" \
     -H "X-AI-Service-Token: your-token" \
     -H "X-AI-Provider: openai" \
     -H "X-AI-Model: gpt-4o-mini" \
     -H "X-AI-API-Key: sk-your-key" \
     -d '{"message": "Test BYOK"}'
   ```

3. **Invalid Token (Should Fail)**
   ```bash
   curl -X POST http://localhost:8000/api/generate-srs \
     -H "Content-Type: application/json" \
     -H "X-AI-Service-Token: invalid-token" \
     -H "X-AI-Provider: openai" \
     -d '{"message": "Test security"}' 
   ```
   Expected: `403 Forbidden`

4. **All Providers**
   - Google: `X-AI-Provider: google`
   - OpenAI: `X-AI-Provider: openai`
   - Anthropic: `X-AI-Provider: anthropic`
   - OpenRouter: `X-AI-Provider: openrouter`

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `403 Forbidden` | Invalid or missing `X-AI-Service-Token` | Provide valid token from `AI_INTERNAL_AUTH_TOKEN` |
| `Unsupported provider` | Unknown provider name | Use: `google`, `openai`, `anthropic`, or `openrouter` |
| `Missing API key` | No key in headers or environment | Set environment variable or provide `X-AI-API-Key` |
| `Invalid API key` | Incorrect key format/value | Verify key is valid for the provider |

### Example Error Response

```json
{
  "detail": "Forbidden: invalid or missing X-AI-Service-Token for model configuration headers."
}
```

---

## Best Practices

### 1. **Security**
- ✅ Always set `AI_INTERNAL_AUTH_TOKEN` in production
- ✅ Use HTTPS for requests with API keys
- ✅ Rotate tokens regularly
- ❌ Never commit API keys to version control

### 2. **Performance**
- ✅ Use `gemini-2.5-flash-lite` for fast, cost-effective responses
- ✅ Cache model instances when possible
- ✅ Use appropriate context window sizes

### 3. **Reliability**
- ✅ Configure fallback providers in environment
- ✅ Implement retry logic for transient failures
- ✅ Monitor API quota/rate limits

### 4. **Development**
- ✅ Test with multiple providers
- ✅ Document provider-specific features
- ✅ Use `.env.example` for team onboarding

---

## FAQ

### Q: Can users choose the provider without a token?
**A:** No. Custom provider/model/key headers require `X-AI-Service-Token` for security. Without custom headers, the system uses default Gemini configuration.

### Q: How do I disable the token requirement?
**A:** Don't set `AI_INTERNAL_AUTH_TOKEN` in your environment. The middleware will skip validation if the token is not configured.

### Q: Can I use different providers for different endpoints?
**A:** Yes! Each request is isolated. You can send different headers to different endpoints.

### Q: What happens if the user's API key fails?
**A:** LangChain will raise an authentication error, which propagates to the client as an HTTP error.

### Q: Is OpenRouter the same as OpenAI?
**A:** OpenRouter is a proxy service that provides access to multiple models (including OpenAI) through a single API. It uses the OpenAI-compatible interface but requires OpenRouter-specific credentials.

---

## Troubleshooting

### Issue: `Module not found: langchain_xxx`

**Solution:**
```bash
pip install langchain-google-genai  # For Google
pip install langchain-openai        # For OpenAI
pip install langchain-anthropic     # For Anthropic
```

### Issue: `ContextVar not working across requests`

**Cause:** Middleware not properly resetting context after request.

**Solution:** Ensure `reset_request_model_config()` is called in `finally` block:
```python
try:
    return await call_next(request)
finally:
    reset_request_model_config(token)
```

### Issue: `OpenRouter returns 401`

**Check:**
1. `OPEN_ROUTER_API_KEY` is set correctly
2. Key has sufficient credits
3. Model name is valid for OpenRouter (e.g., `anthropic/claude-3.5-sonnet`)

---

## Contributing

When modifying the factory pattern:

1. Update this documentation
2. Add tests for new providers
3. Update `requirements.txt` with new dependencies
4. Test backward compatibility
5. Document breaking changes

---

## References

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [Google Gemini API](https://ai.google.dev/docs)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [Anthropic API](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [OpenRouter Documentation](https://openrouter.ai/docs)

---

**Last Updated:** April 6, 2026  
**Version:** 1.0  
**Maintainer:** BA Copilot AI Team
