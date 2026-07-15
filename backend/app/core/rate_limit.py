"""Rate limit de tentativas de login via Redis, conforme 29-SECURITY.md ("Login:
Bloqueio temporário, Detecção de força bruta, Registro de tentativas.") e
16-BACKEND-ARCHITECTURE.md ("Cache: Redis... Rate Limit.")."""

from __future__ import annotations

from functools import lru_cache

from redis.asyncio import Redis

from app.core.config import get_settings


@lru_cache
def get_redis_client() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)


class LoginRateLimiter:
    """Contador de tentativas por chave (ex.: `email:ip`) com janela deslizante simples
    (INCR + EXPIRE). Chamado antes de validar a senha, para nunca revelar se o e-mail
    existe apenas pelo tempo de resposta."""

    def __init__(self, redis_client: Redis) -> None:
        self._redis = redis_client
        self._settings = get_settings()

    async def is_blocked(self, key: str) -> bool:
        attempts = await self._redis.get(self._redis_key(key))
        if attempts is None:
            return False
        return int(attempts) >= self._settings.login_rate_limit_max_attempts

    async def register_failed_attempt(self, key: str) -> None:
        redis_key = self._redis_key(key)
        attempts = await self._redis.incr(redis_key)
        if attempts == 1:
            await self._redis.expire(redis_key, self._settings.login_rate_limit_window_seconds)

    async def reset(self, key: str) -> None:
        await self._redis.delete(self._redis_key(key))

    @staticmethod
    def _redis_key(key: str) -> str:
        return f"login_rate_limit:{key}"


def get_login_rate_limiter() -> LoginRateLimiter:
    return LoginRateLimiter(get_redis_client())
