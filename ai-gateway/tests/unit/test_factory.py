import pytest

from app.core.config import Settings
from app.providers.factory import get_provider
from app.providers.gemini import GeminiProvider


def test_get_provider_returns_gemini_for_google() -> None:
    settings = Settings(_env_file=None, ai_provider="google", gemini_api_key="test-key")  # type: ignore[call-arg]

    provider = get_provider(settings)

    assert isinstance(provider, GeminiProvider)
    assert provider.name == "google"


def test_get_provider_raises_for_unsupported_provider() -> None:
    settings = Settings(_env_file=None, ai_provider="openai")  # type: ignore[call-arg]

    with pytest.raises(NotImplementedError):
        get_provider(settings)
