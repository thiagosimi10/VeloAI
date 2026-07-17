"""Cliente HTTP para o AI Gateway — único ponto por onde o Backend fala com um
provedor de IA, conforme 28-AI-GATEWAY.md ("AI Gateway: ponto único de comunicação com
provedores de LLM."). O Backend nunca chama Gemini/OpenAI/etc diretamente, sempre via
este cliente. Infraestrutura cross-cutting (mesmo nível de `app/core/storage.py`)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from functools import lru_cache
from typing import Any

import httpx
from veloai_shared.exceptions import AppException

from app.core.config import get_settings


@dataclass(frozen=True)
class ToolDeclaration:
    """Espelha `app.schemas.generate.ToolDeclarationDTO` do ai-gateway — conforme
    docs/20-MCP-TOOLS.md ("Estrutura de uma Tool")."""

    name: str
    description: str
    parameters: dict[str, Any]


@dataclass(frozen=True)
class FunctionCall:
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class AIGatewayResult:
    text: str | None
    model: str
    input_tokens: int
    output_tokens: int
    cached: bool
    estimated_cost: Decimal
    function_call: FunctionCall | None = None


class AIGatewayClient:
    def __init__(self, *, base_url: str, timeout_seconds: float = 35.0) -> None:
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        tools: list[ToolDeclaration] | None = None,
    ) -> AIGatewayResult:
        payload: dict[str, Any] = {"prompt": prompt, "system_prompt": system_prompt}
        if tools:
            payload["tools"] = [
                {"name": tool.name, "description": tool.description, "parameters": tool.parameters}
                for tool in tools
            ]

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

        function_call_data = data.get("function_call")
        function_call = (
            FunctionCall(name=function_call_data["name"], arguments=function_call_data["arguments"])
            if function_call_data is not None
            else None
        )

        return AIGatewayResult(
            text=data["text"],
            model=data["model"],
            input_tokens=data["input_tokens"],
            output_tokens=data["output_tokens"],
            cached=data["cached"],
            estimated_cost=Decimal(str(data["estimated_cost"])),
            function_call=function_call,
        )

    async def embeddings(self, texts: list[str]) -> list[list[float]]:
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(
                    f"{self._base_url}/embeddings", json={"texts": texts}
                )
                response.raise_for_status()
                data = response.json()["data"]
        except httpx.HTTPError as exc:
            raise AppException(
                "Falha ao consultar o assistente de IA. Tente novamente em instantes.",
                code="AI_GATEWAY_ERROR",
                status_code=502,
            ) from exc

        return data["embeddings"]


@lru_cache
def get_ai_gateway_client() -> AIGatewayClient:
    """Retorna a instância única (cacheada) de `AIGatewayClient`, mesmo padrão de
    `get_settings()`/`get_storage_client()`."""

    settings = get_settings()
    return AIGatewayClient(base_url=settings.ai_gateway_url)
