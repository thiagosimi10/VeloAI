import httpx
import pytest
import respx

from app.providers.gemini import GeminiProvider

_MODEL = "gemini-3.1-flash-lite"
_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{_MODEL}:generateContent"


@respx.mock
async def test_generate_parses_successful_response() -> None:
    respx.post(_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "candidates": [{"content": {"parts": [{"text": "Olá, humano!"}]}}],
                "usageMetadata": {"promptTokenCount": 5, "candidatesTokenCount": 3},
            },
        )
    )
    provider = GeminiProvider(api_key="fake-key", model=_MODEL)

    result = await provider.generate("Diga olá.")

    assert result.text == "Olá, humano!"
    assert result.input_tokens == 5
    assert result.output_tokens == 3
    assert result.model == _MODEL


@respx.mock
async def test_generate_falls_back_to_estimated_tokens_when_usage_missing() -> None:
    respx.post(_URL).mock(
        return_value=httpx.Response(
            200,
            json={"candidates": [{"content": {"parts": [{"text": "ok"}]}}]},
        )
    )
    provider = GeminiProvider(api_key="fake-key", model=_MODEL)

    result = await provider.generate("prompt de teste")

    assert result.text == "ok"
    assert result.input_tokens > 0
    assert result.output_tokens > 0


@respx.mock
async def test_generate_raises_when_no_candidates_returned() -> None:
    respx.post(_URL).mock(return_value=httpx.Response(200, json={"candidates": []}))
    provider = GeminiProvider(api_key="fake-key", model=_MODEL)

    with pytest.raises(RuntimeError):
        await provider.generate("prompt")


@respx.mock
async def test_generate_raises_on_http_error() -> None:
    respx.post(_URL).mock(return_value=httpx.Response(500, json={"error": "boom"}))
    provider = GeminiProvider(api_key="fake-key", model=_MODEL)

    with pytest.raises(httpx.HTTPStatusError):
        await provider.generate("prompt")


async def test_health_check_true_when_api_key_present() -> None:
    provider = GeminiProvider(api_key="fake-key", model=_MODEL)

    assert await provider.health_check() is True


async def test_health_check_false_when_api_key_missing() -> None:
    provider = GeminiProvider(api_key="", model=_MODEL)

    assert await provider.health_check() is False


async def test_list_models_returns_configured_model() -> None:
    provider = GeminiProvider(api_key="fake-key", model=_MODEL)

    assert await provider.list_models() == [_MODEL]


async def test_embeddings_not_implemented_yet() -> None:
    provider = GeminiProvider(api_key="fake-key", model=_MODEL)

    with pytest.raises(NotImplementedError):
        await provider.embeddings(["texto"])


def test_estimate_cost_scales_with_token_counts() -> None:
    provider = GeminiProvider(api_key="fake-key", model=_MODEL)

    cost_small = provider.estimate_cost(1000, 1000)
    cost_large = provider.estimate_cost(2000, 2000)

    assert cost_small > 0
    assert cost_large == cost_small * 2


def test_estimate_cost_zero_tokens_is_zero() -> None:
    provider = GeminiProvider(api_key="fake-key", model=_MODEL)

    assert provider.estimate_cost(0, 0) == 0
