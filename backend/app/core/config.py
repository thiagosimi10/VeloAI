"""Configuração do Backend via variáveis de ambiente (Pydantic Settings), conforme
16-BACKEND-ARCHITECTURE.md ("Utilizar .env, Pydantic Settings. Nunca utilizar valores
fixos.")."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "VeloAI Backend"
    app_env: str = "development"
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"
    cors_allowed_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Retorna a instância única (cacheada) de `Settings`."""

    return Settings()
