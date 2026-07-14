"""Configuração do AI Gateway, conforme 28-AI-GATEWAY.md e 03-STACK-TECNOLOGICA.md."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "VeloAI AI Gateway"
    app_env: str = "development"
    log_level: str = "INFO"

    ai_provider: str = "google"
    ai_report_model: str = "gemini-3.1-flash-lite"
    gemini_api_key: str = ""
    ai_temperature: float = 0.2
    ai_max_tokens: int = 8192


@lru_cache
def get_settings() -> Settings:
    return Settings()
