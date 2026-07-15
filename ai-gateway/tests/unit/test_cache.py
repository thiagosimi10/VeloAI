from fakeredis import aioredis as fakeredis_aioredis

from app.core.cache import build_cache_key, get_cached_response, set_cached_response
from app.providers.base import GenerateResult


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
