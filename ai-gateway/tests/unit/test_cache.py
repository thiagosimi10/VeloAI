from fakeredis import aioredis as fakeredis_aioredis

from app.core.cache import build_cache_key, get_cached_response, set_cached_response
from app.providers.base import FunctionCallResult, GenerateResult, ToolDeclaration


def test_build_cache_key_is_deterministic() -> None:
    key_1 = build_cache_key("gemini-3.1-flash-lite", "system", "prompt")
    key_2 = build_cache_key("gemini-3.1-flash-lite", "system", "prompt")

    assert key_1 == key_2


def test_build_cache_key_differs_by_prompt() -> None:
    key_1 = build_cache_key("gemini-3.1-flash-lite", "system", "prompt a")
    key_2 = build_cache_key("gemini-3.1-flash-lite", "system", "prompt b")

    assert key_1 != key_2


def test_build_cache_key_treats_missing_system_prompt_consistently() -> None:
    key_1 = build_cache_key("gemini-3.1-flash-lite", None, "prompt")
    key_2 = build_cache_key("gemini-3.1-flash-lite", None, "prompt")

    assert key_1 == key_2


async def test_get_cached_response_is_none_on_miss() -> None:
    fake_redis = fakeredis_aioredis.FakeRedis(decode_responses=True)

    result = await get_cached_response(fake_redis, "missing-key")

    assert result is None


async def test_set_then_get_round_trips_result() -> None:
    fake_redis = fakeredis_aioredis.FakeRedis(decode_responses=True)
    key = build_cache_key("gemini-3.1-flash-lite", "system", "prompt")
    original = GenerateResult(
        text="resposta", input_tokens=5, output_tokens=3, model="gemini-3.1-flash-lite"
    )

    await set_cached_response(fake_redis, key, original, ttl_seconds=60)
    cached = await get_cached_response(fake_redis, key)

    assert cached == original


async def test_set_then_get_round_trips_function_call() -> None:
    fake_redis = fakeredis_aioredis.FakeRedis(decode_responses=True)
    key = build_cache_key("gemini-3.1-flash-lite", "system", "prompt")
    original = GenerateResult(
        text=None,
        input_tokens=12,
        output_tokens=8,
        model="gemini-3.1-flash-lite",
        function_call=FunctionCallResult(name="CreateCustomer", arguments={"name": "João Silva"}),
    )

    await set_cached_response(fake_redis, key, original, ttl_seconds=60)
    cached = await get_cached_response(fake_redis, key)

    assert cached == original


def test_build_cache_key_differs_by_tools() -> None:
    tool = ToolDeclaration(name="SearchCustomers", description="Busca", parameters={})

    key_without_tools = build_cache_key("gemini-3.1-flash-lite", "system", "prompt")
    key_with_tools = build_cache_key("gemini-3.1-flash-lite", "system", "prompt", [tool])

    assert key_without_tools != key_with_tools


def test_build_cache_key_differs_by_tool_parameters() -> None:
    tool_a = ToolDeclaration(name="SearchCustomers", description="Busca", parameters={"a": 1})
    tool_b = ToolDeclaration(name="SearchCustomers", description="Busca", parameters={"a": 2})

    key_a = build_cache_key("gemini-3.1-flash-lite", "system", "prompt", [tool_a])
    key_b = build_cache_key("gemini-3.1-flash-lite", "system", "prompt", [tool_b])

    assert key_a != key_b
