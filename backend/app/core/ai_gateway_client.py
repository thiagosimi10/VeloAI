"""Cliente HTTP para o AI Gateway — único ponto por onde o Backend fala com um
provedor de IA, conforme 28-AI-GATEWAY.md ("AI Gateway: ponto único de comunicação com
provedores de LLM."). O Backend nunca chama Gemini/OpenAI/etc diretamente, sempre via
este cliente. Infraestrutura cross-cutting (mesmo nível de `app/core/storage.py`)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from functools import lru_cache

import httpx
from veloai_shared.exceptions import AppException

from app.core.config import get_settings


@dataclass(frozen=True)
class AIGatewayResult:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    cached: bool
    estimated_cost: Decimal


class AIGatewayClient:
    def __init__(self, *, base_url: str, timeout_seconds: float = 35.0) -> None:
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds

    async def generate(self, prompt: str, *, system_prompt: str | None = None) -> AIGatewayResult:
        payload = {"prompt": prompt, "system_prompt": system_prompt}

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(f"{self._base_url}/generate", json=payload)
                response.raise_for_status()
                data = response.json()["data"]
        except httpx.HTTPError as exc:
            raise AppException(
                "Falha ao consultar o assistente de IA. Tente novamente em instantes.",
                code="AI_GATEWAY_ERROR",
                status_code=502,
            ) from exc

        return AIGatewayResult(
            text=data["text"],
            model=data["model"],
            input_tokens=data["input_tokens"],
            output_tokens=data["output_tokens"],
            cached=data["cached"],
            estimated_cost=Decimal(str(data["estimated_cost"])),
        )


@lru_cache
def get_ai_gateway_client() -> AIGatewayClient:
    """Retorna a instância única (cacheada) de `AIGatewayClient`, mesmo padrão de
    `get_settings()`/`get_storage_client()`."""

    settings = get_settings()
    return AIGatewayClient(base_url=settings.ai_gateway_url)
