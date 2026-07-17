"""Provider Gemini (Google AI), o provedor inicial oficial do VeloAI, conforme
01-VISAO-GERAL.md e 03-STACK-TECNOLOGICA.md (`AI_REPORT_MODEL=gemini-3.1-flash-lite`)."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import httpx

from app.providers.base import AIProvider, FunctionCallResult, GenerateResult, ToolDeclaration

_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

# Gemini usa um subconjunto de OpenAPI Schema com os valores de "type" em maiúsculo
# (STRING/INTEGER/NUMBER/BOOLEAN/OBJECT/ARRAY), diferente do JSON Schema padrão (que
# `BaseModel.model_json_schema()` do Pydantic produz em minúsculo).
_JSON_SCHEMA_TYPE_TO_GEMINI = {
    "string": "STRING",
    "integer": "INTEGER",
    "number": "NUMBER",
    "boolean": "BOOLEAN",
    "object": "OBJECT",
    "array": "ARRAY",
}


def _to_gemini_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Converte um JSON Schema no formato do Pydantic v2 (`model_json_schema()`) para o
    formato de `parameters` exigido pelo Gemini. Pydantic v2 representa um campo
    opcional (`str | None` com default) como `{"anyOf": [{"type": "string"}, {"type":
    "null"}]}` — Gemini não entende `anyOf`, então pegamos o primeiro branch não-nulo.
    Assume schemas simples (sem `$ref`/`$defs`), que é o caso de todo `input_model` de
    Tool nesta fase (campos escalares, sem sub-modelos aninhados)."""

    if "anyOf" in schema:
        non_null = [branch for branch in schema["anyOf"] if branch.get("type") != "null"]
        converted = _to_gemini_schema(non_null[0]) if non_null else {"type": "STRING"}
        if "description" in schema:
            converted["description"] = schema["description"]
        return converted

    result: dict[str, Any] = {}
    if "type" in schema:
        result["type"] = _JSON_SCHEMA_TYPE_TO_GEMINI.get(schema["type"], schema["type"].upper())
    if "description" in schema:
        result["description"] = schema["description"]
    if "enum" in schema:
        result["enum"] = schema["enum"]
    if "properties" in schema:
        result["properties"] = {
            name: _to_gemini_schema(value) for name, value in schema["properties"].items()
        }
    if "required" in schema:
        result["required"] = schema["required"]
    if "items" in schema:
        result["items"] = _to_gemini_schema(schema["items"])
    return result


def _to_gemini_function_declaration(tool: ToolDeclaration) -> dict[str, Any]:
    return {
        "name": tool.name,
        "description": tool.description,
        "parameters": _to_gemini_schema(tool.parameters),
    }


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
        embedding_model: str = "text-embedding-004",
        temperature: float = 0.2,
        max_output_tokens: int = 8192,
        timeout_seconds: float = 30.0,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._embedding_model = embedding_model
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens
        self._timeout_seconds = timeout_seconds

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        tools: list[ToolDeclaration] | None = None,
    ) -> GenerateResult:
        payload: dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self._temperature,
                "maxOutputTokens": self._max_output_tokens,
            },
        }
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        if tools:
            payload["tools"] = [
                {"functionDeclarations": [_to_gemini_function_declaration(tool) for tool in tools]}
            ]

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
        usage = data.get("usageMetadata", {})

        function_call_part = next(
            (part["functionCall"] for part in parts if "functionCall" in part), None
        )
        if function_call_part is not None:
            return GenerateResult(
                text=None,
                function_call=FunctionCallResult(
                    name=function_call_part["name"], arguments=function_call_part.get("args", {})
                ),
                input_tokens=usage.get("promptTokenCount") or self.count_tokens(prompt),
                output_tokens=usage.get("candidatesTokenCount") or 0,
                model=self._model,
            )

        text = "".join(part.get("text", "") for part in parts)
        return GenerateResult(
            text=text,
            function_call=None,
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

    async def embeddings(self, texts: list[str]) -> list[list[float]]:
        url = f"{_GEMINI_BASE_URL}/models/{self._embedding_model}:batchEmbedContents"
        payload = {
            "requests": [
                {
                    "model": f"models/{self._embedding_model}",
                    "content": {"parts": [{"text": text}]},
                }
                for text in texts
            ]
        }

        async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
            response = await client.post(url, params={"key": self._api_key}, json=payload)
            response.raise_for_status()
            data = response.json()

        return [item["values"] for item in data.get("embeddings", [])]

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        input_cost = (Decimal(input_tokens) / 1000) * _PRICE_PER_1K_INPUT_TOKENS
        output_cost = (Decimal(output_tokens) / 1000) * _PRICE_PER_1K_OUTPUT_TOKENS
        return input_cost + output_cost
