import pytest
from types import SimpleNamespace


from src.services.llm_service import LLMService


class FakeOpenRouterClient:
    def __init__(self, content: str, capture_kwargs: bool = False, raise_error: bool = False):
        self._content = content
        self._capture = capture_kwargs
        self._raise = raise_error
        self.last_kwargs = None

    class _Chat:
        class _Completions:
            def __init__(self, outer):
                self._outer = outer

            async def create(self, **kwargs):
                if self._outer._capture:
                    self._outer.last_kwargs = kwargs
                if self._outer._raise:
                    raise RuntimeError("simulated error")
                # Build a minimal OpenAI-like response object
                message = SimpleNamespace(content=self._outer._content)
                choice = SimpleNamespace(message=message)
                return SimpleNamespace(choices=[choice])

        def __init__(self, outer):
            self.completions = FakeOpenRouterClient._Chat._Completions(outer)

    @property
    def chat(self):
        return FakeOpenRouterClient._Chat(self)


class FakeGoogleModel:
    def __init__(self, text: str):
        self._text = text

    def generate_content(self, prompt: str):
        return SimpleNamespace(text=self._text)


@pytest.mark.asyncio
async def test_generate_srs_openrouter_parses_json_and_sets_headers():
    # Arrange
    svc = LLMService()

    # Force provider to openrouter and inject fake client
    def fake_init():
        svc.provider = "openrouter"
        svc.client = FakeOpenRouterClient(
            content='```json\n{"title":"X","version":"1.0"}\n```',
            capture_kwargs=True,
        )
        svc._initialized = True

    svc._ensure_initialized = fake_init  # type: ignore

    # Set headers for extra_headers path using the same settings object referenced by the service module
    from src.services import llm_service as llm_mod
    llm_mod.settings.openrouter_referer = "https://example.com"
    llm_mod.settings.openrouter_title = "BA Copilot Tests"

    # Act
    result = await svc.generate_srs_document("any input that is long enough")

    # Assert
    assert result["title"] == "X"
    # Validate model id and headers used
    called = getattr(svc.client, "last_kwargs", None)
    assert called is not None
    assert called.get("model") == "deepseek/deepseek-chat-v3.1:free"
    headers = called.get("extra_headers")
    assert isinstance(headers, dict)
    assert headers.get("HTTP-Referer") == "https://example.com"
    assert headers.get("X-Title") == "BA Copilot Tests"


@pytest.mark.asyncio
async def test_generate_srs_google_non_json_fallback_with_raw_response():
    # Arrange
    svc = LLMService()

    def fake_init():
        svc.provider = "google"
        svc.model = FakeGoogleModel(text="this is not json")
        svc._initialized = True

    svc._ensure_initialized = fake_init  # type: ignore

    # Act
    result = await svc.generate_srs_document("generate document")

    # Assert fallback with raw_response included
    assert result["title"].startswith("Generated SRS Document")
    assert "raw_response" in result
    assert result["raw_response"] == "this is not json"


@pytest.mark.asyncio
async def test_generate_srs_openrouter_empty_content_triggers_outer_fallback():
    # Arrange
    svc = LLMService()

    def fake_init():
        svc.provider = "openrouter"
        svc.client = FakeOpenRouterClient(content="")
        svc._initialized = True

    svc._ensure_initialized = fake_init  # type: ignore

    # Act
    result = await svc.generate_srs_document("some input")

    # Assert: fallback without raw_response key
    assert result["title"].startswith("Generated SRS Document")
    assert "raw_response" not in result


@pytest.mark.asyncio
async def test_generate_srs_fallback_provider_returns_document():
    # Arrange
    svc = LLMService()

    def fake_init():
        svc.provider = "fallback"
        svc._initialized = True

    svc._ensure_initialized = fake_init  # type: ignore

    # Act
    result = await svc.generate_srs_document("fallback journey")

    # Assert
    assert result["title"].startswith("Generated SRS Document")
    assert result["version"] == "1.0"


@pytest.mark.asyncio
async def test_generate_content_openrouter_success():
    svc = LLMService()

    def fake_init():
        svc.provider = "openrouter"
        svc.client = FakeOpenRouterClient(content="ok")
        svc._initialized = True

    svc._ensure_initialized = fake_init  # type: ignore

    text = await svc.generate_content("hello")
    assert text == "ok"


@pytest.mark.asyncio
async def test_generate_content_google_success():
    svc = LLMService()

    def fake_init():
        svc.provider = "google"
        svc.model = FakeGoogleModel(text="ok")
        svc._initialized = True

    svc._ensure_initialized = fake_init  # type: ignore

    text = await svc.generate_content("hello")
    assert text == "ok"


@pytest.mark.asyncio
async def test_generate_content_error_returns_prompt():
    svc = LLMService()

    def fake_init():
        svc.provider = "openrouter"
        svc.client = FakeOpenRouterClient(content="", raise_error=True)
        svc._initialized = True

    svc._ensure_initialized = fake_init  # type: ignore

    text = await svc.generate_content("keep this")
    assert text == "keep this"
