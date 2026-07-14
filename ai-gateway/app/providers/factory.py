"""Fábrica de provedores de IA — a troca de provedor ocorre apenas por configuração
(`AI_PROVIDER`), conforme 01-VISAO-GERAL.md ("A troca de provedor deverá ocorrer apenas
por configuração.").

Apenas o provider `google` (Gemini) está implementado nesta fase. A arquitetura já está
preparada para OpenAI, Claude, DeepSeek, Ollama e Bedrock (ver docs/28-AI-GATEWAY.md) —
adicioná-los exige apenas uma nova classe em `app/providers/` e um novo `elif` aqui,
sem alterar nenhum consumidor desta fábrica."""

from __future__ import annotations

from app.core.config import Settings
from app.providers.base import AIProvider
from app.providers.gemini import GeminiProvider

_SUPPORTED_PROVIDERS = ("google",)


def get_provider(settings: Settings) -> AIProvider:
    if settings.ai_provider == "google":
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.ai_report_model,
            temperature=settings.ai_temperature,
            max_output_tokens=settings.ai_max_tokens,
        )

    raise NotImplementedError(
        f"Provider de IA '{settings.ai_provider}' ainda não implementado. "
        f"Providers suportados nesta fase: {_SUPPORTED_PROVIDERS}."
    )
