"""Interface comum a todo provedor de IA, conforme 28-AI-GATEWAY.md ("Cada Provider
deverá possuir: Generate, Streaming, Embeddings, Health Check, Estimate Cost, List
Models, Count Tokens. Todos implementarão a mesma interface.").

Nesta fase de fundação apenas o Gemini é implementado por completo. `embeddings` e
`estimate_cost` fazem parte da interface (arquitetura preparada), mas levantam
`NotImplementedError` — RAG (embeddings) e Billing de IA (custo) são fases futuras do
Master Plan."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class GenerateResult:
    text: str
    input_tokens: int
    output_tokens: int
    model: str


class AIProvider(ABC):
    """Todo novo provedor (OpenAI, Claude, DeepSeek, Ollama, Bedrock...) deve herdar
    desta classe e implementar, no mínimo, `generate` e `health_check`."""

    name: str

    @abstractmethod
    async def generate(self, prompt: str, *, system_prompt: str | None = None) -> GenerateResult:
        """Gera uma resposta de texto a partir de um prompt."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Indica se o provedor está configurado e apto a responder requisições."""

    @abstractmethod
    async def list_models(self) -> list[str]:
        """Lista os modelos disponíveis para este provedor."""

    def count_tokens(self, text: str) -> int:
        """Estimativa aproximada de tokens (1 token ≈ 4 caracteres). Usada apenas como
        fallback quando o provedor não retorna a contagem exata na resposta."""

        return max(1, len(text) // 4)

    async def embeddings(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError(
            f"Provider '{self.name}' ainda não implementa embeddings — RAG é uma fase "
            "futura do Master Plan (ver docs/21-RAG.md)."
        )

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        raise NotImplementedError(
            f"Provider '{self.name}' ainda não implementa estimativa de custo — Billing "
            "de IA é uma fase futura do Master Plan (ver docs/28-AI-GATEWAY.md)."
        )
