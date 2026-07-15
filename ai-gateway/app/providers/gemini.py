"""Provider Gemini (Google AI), o provedor inicial oficial do VeloAI, conforme
01-VISAO-GERAL.md e 03-STACK-TECNOLOGICA.md (`AI_REPORT_MODEL=gemini-3.1-flash-lite`)."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import httpx

from app.providers.base import AIProvider, GenerateResult

_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

# Preços aproximados por 1K tokens do gemini-3.1-flash-lite, apenas para estimativa —
# não é fatura real (integração de cobrança de verdade é uma fase própria, ver
# docs/31-BILLING.md). Ajustar caso o modelo configurado mude de faixa de preço.
_PRICE_PER_1K_INPUT_TOKENS = Decimal("0.00010")
_PRICE_PER_1K_OUTPUT_TOKENS = Decimal("0.00040")


class GeminiProvider(AIProvider):
    name = "google"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        temperature: float = 0.2,
        max_output_tokens: int = 8192,
        timeout_seconds: float = 30.0,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens
        self._timeout_seconds = timeout_seconds

    async def generate(self, prompt: str, *, system_prompt: str | None = None) -> GenerateResult:
        payload: dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self._temperature,
                "maxOutputTokens": self._max_output_tokens,
            },
        }
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        url = f"{_GEMINI_BASE_URL}/models/{self._model}:generateContent"

        async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
            response = await client.post(url, params={"key": self._api_key}, json=payload)
            response.raise_for_status()
            data = response.json()

        return self._parse_response(data, prompt)

    def _parse_response(self, data: dict[str, Any], prompt: str) -> GenerateResult:
        candidates = data.get("candidates") or []
        if not candidates:
            raise RuntimeError("Gemini não retornou nenhum candidato de resposta.")

        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts)

        usage = data.get("usageMetadata", {})
        return GenerateResult(
            text=text,
            input_tokens=usage.get("promptTokenCount") or self.count_tokens(prompt),
            output_tokens=usage.get("candidatesTokenCount") or self.count_tokens(text),
            model=self._model,
        )

    async def health_check(self) -> bool:
        """Verifica apenas se o provedor está configurado (chave presente). Não realiza
        chamada de rede a cada checagem de readiness para não consumir cota da API."""

        return bool(self._api_key)

    async def list_models(self) -> list[str]:
        return [self._model]

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        input_cost = (Decimal(input_tokens) / 1000) * _PRICE_PER_1K_INPUT_TOKENS
        output_cost = (Decimal(output_tokens) / 1000) * _PRICE_PER_1K_OUTPUT_TOKENS
        return input_cost + output_cost
