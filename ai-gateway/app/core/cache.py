"""Cache de respostas do `/generate` via Redis (Response Cache), conforme
28-AI-GATEWAY.md ("Cache: ... Response Cache"). Isolado no próprio ai-gateway — o
serviço continua sem depender de Postgres, só de um Redis. Compartilha a mesma
instância/índice já usado pelo Backend para rate limit de login (um único `REDIS_URL`
no `.env` raiz, aplicado a todos os serviços via `env_file`) — isolado por
key-prefixing (`ai_gateway:generate:...`), mesmo padrão já usado no projeto
(`login_rate_limit:...`) em vez de banco por índice."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache

from redis.asyncio import Redis

from app.core.config import get_settings
from app.providers.base import FunctionCallResult, GenerateResult, ToolDeclaration


@lru_cache
def get_redis_client() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)


def build_cache_key(
    model: str,
    system_prompt: str | None,
    prompt: str,
    tools: list[ToolDeclaration] | None = None,
) -> str:
    """Inclui as Tools disponíveis na chave — a mesma pergunta pode ter respostas
    diferentes (com ou sem chamada de função) dependendo de quais Tools o usuário tem
    permissão para usar, então a chave precisa variar por isso também (Fase 14),
    além de `model`/`system_prompt`/`prompt` (que já variam por empresa/usuário)."""

    tools_fingerprint = json.dumps(
        [{"name": tool.name, "parameters": tool.parameters} for tool in (tools or [])],
        sort_keys=True,
    )
    digest_input = (
        f"{model}\x1f{system_prompt or ''}\x1f{prompt}\x1f{tools_fingerprint}".encode()
    )
    return f"ai_gateway:generate:{hashlib.sha256(digest_input).hexdigest()}"


async def get_cached_response(redis_client: Redis, key: str) -> GenerateResult | None:
    raw = await redis_client.get(key)
    if raw is None:
        return None
    data = json.loads(raw)
    function_call_data = data.pop("function_call", None)
    function_call = FunctionCallResult(**function_call_data) if function_call_data else None
    return GenerateResult(**data, function_call=function_call)


async def set_cached_response(
    redis_client: Redis, key: str, result: GenerateResult, *, ttl_seconds: int
) -> None:
    function_call = result.function_call
    payload = json.dumps(
        {
            "text": result.text,
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "model": result.model,
            "function_call": (
                {"name": function_call.name, "arguments": function_call.arguments}
                if function_call is not None
                else None
            ),
        }
    )
    await redis_client.set(key, payload, ex=ttl_seconds)
