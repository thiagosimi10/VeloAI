import pytest
from fakeredis import aioredis as fakeredis_aioredis

from app.core.config import Settings
from app.core.rate_limit import SignupRateLimiter


@pytest.fixture
def settings() -> Settings:
    return Settings(
        _env_file=None,  # type: ignore[call-arg]
        signup_rate_limit_max_attempts=3,
        signup_rate_limit_window_seconds=60,
    )


@pytest.fixture
async def rate_limiter(settings: Settings) -> SignupRateLimiter:
    fake_redis = fakeredis_aioredis.FakeRedis(decode_responses=True)
    limiter = SignupRateLimiter(fake_redis)
    limiter._settings = settings  # type: ignore[attr-defined]
    return limiter


async def test_is_blocked_false_when_no_attempts_yet(rate_limiter: SignupRateLimiter) -> None:
    assert await rate_limiter.is_blocked("1.2.3.4") is False


async def test_becomes_blocked_after_max_attempts(rate_limiter: SignupRateLimiter) -> None:
    key = "1.2.3.4"

    for _ in range(3):
        await rate_limiter.register_attempt(key)

    assert await rate_limiter.is_blocked(key) is True


async def test_not_blocked_before_reaching_max_attempts(rate_limiter: SignupRateLimiter) -> None:
    key = "1.2.3.4"

    await rate_limiter.register_attempt(key)
    await rate_limiter.register_attempt(key)

    assert await rate_limiter.is_blocked(key) is False


async def test_different_keys_are_independent(rate_limiter: SignupRateLimiter) -> None:
    await rate_limiter.register_attempt("1.1.1.1")
    await rate_limiter.register_attempt("1.1.1.1")
    await rate_limiter.register_attempt("1.1.1.1")

    assert await rate_limiter.is_blocked("1.1.1.1") is True
    assert await rate_limiter.is_blocked("2.2.2.2") is False
