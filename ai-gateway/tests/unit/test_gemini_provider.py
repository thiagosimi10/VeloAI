import json

import httpx
import pytest
import respx

from app.providers.base import ToolDeclaration
from app.providers.gemini import GeminiProvider, _to_gemini_schema

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


_EMBEDDING_MODEL = "text-embedding-004"
_EMBEDDINGS_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{_EMBEDDING_MODEL}:batchEmbedContents"
)


@respx.mock
async def test_embeddings_parses_successful_response() -> None:
    respx.post(_EMBEDDINGS_URL).mock(
        return_value=httpx.Response(
            200,
            json={"embeddings": [{"values": [0.1, 0.2, 0.3]}, {"values": [0.4, 0.5, 0.6]}]},
        )
    )
    provider = GeminiProvider(
        api_key="fake-key", model=_MODEL, embedding_model=_EMBEDDING_MODEL
    )

    result = await provider.embeddings(["texto um", "texto dois"])

    assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]


@respx.mock
async def test_embeddings_sends_one_request_per_text() -> None:
    route = respx.post(_EMBEDDINGS_URL).mock(
        return_value=httpx.Response(200, json={"embeddings": [{"values": [0.1]}]})
    )
    provider = GeminiProvider(
        api_key="fake-key", model=_MODEL, embedding_model=_EMBEDDING_MODEL
    )

    await provider.embeddings(["único texto"])

    sent_payload = json.loads(route.calls.last.request.content)
    assert len(sent_payload["requests"]) == 1
    assert sent_payload["requests"][0]["model"] == f"models/{_EMBEDDING_MODEL}"
    assert sent_payload["requests"][0]["content"]["parts"][0]["text"] == "único texto"


def test_estimate_cost_scales_with_token_counts() -> None:
    provider = GeminiProvider(api_key="fake-key", model=_MODEL)

    cost_small = provider.estimate_cost(1000, 1000)
    cost_large = provider.estimate_cost(2000, 2000)

    assert cost_small > 0
    assert cost_large == cost_small * 2


def test_estimate_cost_zero_tokens_is_zero() -> None:
    provider = GeminiProvider(api_key="fake-key", model=_MODEL)

    assert provider.estimate_cost(0, 0) == 0


@respx.mock
async def test_generate_sends_tool_declarations_to_gemini() -> None:
    route = respx.post(_URL).mock(
        return_value=httpx.Response(
            200, json={"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}
        )
    )
    provider = GeminiProvider(api_key="fake-key", model=_MODEL)
    tool = ToolDeclaration(
        name="SearchCustomers",
        description="Busca clientes cadastrados.",
        parameters={
            "type": "object",
            "properties": {
                "search": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None}
            },
        },
    )

    await provider.generate("Busque o cliente João", tools=[tool])

    sent_payload = json.loads(route.calls.last.request.content)
    declarations = sent_payload["tools"][0]["functionDeclarations"]
    assert declarations[0]["name"] == "SearchCustomers"
    assert declarations[0]["parameters"]["properties"]["search"]["type"] == "STRING"


@respx.mock
async def test_generate_omits_tools_key_when_none_provided() -> None:
    route = respx.post(_URL).mock(
        return_value=httpx.Response(
            200, json={"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}
        )
    )
    provider = GeminiProvider(api_key="fake-key", model=_MODEL)

    await provider.generate("prompt sem tools")

    sent_payload = json.loads(route.calls.last.request.content)
    assert "tools" not in sent_payload


@respx.mock
async def test_generate_returns_function_call_when_gemini_requests_one() -> None:
    respx.post(_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "functionCall": {
                                        "name": "CreateCustomer",
                                        "args": {"name": "João Silva"},
                                    }
                                }
                            ]
                        }
                    }
                ],
                "usageMetadata": {"promptTokenCount": 12, "candidatesTokenCount": 8},
            },
        )
    )
    provider = GeminiProvider(api_key="fake-key", model=_MODEL)

    result = await provider.generate("Cadastre um cliente chamado João Silva.")

    assert result.text is None
    assert result.function_call is not None
    assert result.function_call.name == "CreateCustomer"
    assert result.function_call.arguments == {"name": "João Silva"}
    assert result.input_tokens == 12
    assert result.output_tokens == 8


def test_to_gemini_schema_converts_types_to_uppercase() -> None:
    schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "quantity": {"type": "integer"}},
        "required": ["name"],
    }

    converted = _to_gemini_schema(schema)

    assert converted["type"] == "OBJECT"
    assert converted["properties"]["name"]["type"] == "STRING"
    assert converted["properties"]["quantity"]["type"] == "INTEGER"
    assert converted["required"] == ["name"]


def test_to_gemini_schema_resolves_anyof_optional_field() -> None:
    schema = {
        "type": "object",
        "properties": {
            "email": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "default": None,
                "description": "E-mail do cliente",
            }
        },
    }

    converted = _to_gemini_schema(schema)

    assert converted["properties"]["email"]["type"] == "STRING"
    assert converted["properties"]["email"]["description"] == "E-mail do cliente"
