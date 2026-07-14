"""Configuração do Provisioning Service, conforme 19-PROVISIONING-SERVICE.md.

Este é o único serviço do VeloAI autorizado a possuir credenciais administrativas do
PostgreSQL (CREATE DATABASE / DROP DATABASE / CREATE SCHEMA) — ver 29-SECURITY.md."""

from __future__ import annotations

from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "VeloAI Provisioning"
    app_env: str = "development"
    log_level: str = "INFO"

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_user: str = "veloai_admin"
    postgres_password: str = "change-me-in-production"
    postgres_maintenance_db: str = "postgres"

    database_master_url: str = (
        "postgresql+asyncpg://veloai_admin:change-me-in-production@postgres:5432/veloai_master"
    )

    tenant_database_prefix: str = "tenant_"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def maintenance_database_url(self) -> str:
        """URL de conexão à base de manutenção (`postgres`), usada exclusivamente para
        emitir `CREATE DATABASE` / `DROP DATABASE`. Nunca armazena dados de negócio."""

        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_maintenance_db}"
        )

    def tenant_database_url(self, database_name: str) -> str:
        """Monta a URL de conexão para o banco exclusivo de um tenant já criado."""

        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{database_name}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
