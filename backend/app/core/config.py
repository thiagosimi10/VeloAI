"""Configuração do Backend via variáveis de ambiente (Pydantic Settings), conforme
16-BACKEND-ARCHITECTURE.md ("Utilizar .env, Pydantic Settings. Nunca utilizar valores
fixos.").

O Backend nunca possui credenciais administrativas de banco (29-SECURITY.md) — apenas
a role de aplicação `veloai_app`, criada e concedida pelo Provisioning Service."""

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

    # PostgreSQL — sempre autenticando como `veloai_app` (nunca a role administrativa).
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_master_db: str = "veloai_master"
    postgres_app_user: str = "veloai_app"
    postgres_app_password: str = "change-me-in-production"

    # Redis (cache, sessões, rate limit).
    redis_url: str = "redis://redis:6379/0"

    # JWT / Cookies.
    jwt_secret: str = "change-me-in-production"
    jwt_refresh_secret: str = "change-me-in-production"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 14
    cookie_secure: bool = False

    # Painel Administrativo (Fase 18) — secret próprio, nunca reaproveita jwt_secret
    # (isola a assinatura dos tokens de Platform Admin dos tokens de sessão de tenant).
    platform_admin_jwt_secret: str = "change-me-in-production"
    platform_admin_token_expire_minutes: int = 60

    # Rate limit de login (29-SECURITY.md, "Login: bloqueio temporário").
    login_rate_limit_max_attempts: int = 5
    login_rate_limit_window_seconds: int = 900

    # MinIO (Storage — Fase 12, anexos genéricos).
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "veloai_minio"
    minio_secret_key: str = "change-me-in-production"
    minio_use_ssl: bool = False
    minio_bucket_name: str = "veloai-attachments"

    # AI Gateway (Fase 13) — único serviço que o Backend chama para falar com uma LLM.
    ai_gateway_url: str = "http://ai-gateway:8002"

    # Qdrant (RAG — Fase 15): uma Collection por tenant, conforme 04-MULTI-TENANCY.md.
    qdrant_url: str = "http://qdrant:6333"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    @property
    def master_database_url(self) -> str:
        """URL de conexão ao Banco Master usando a role de aplicação (somente leitura
        de tabelas de roteamento — nunca DDL)."""

        return (
            f"postgresql+asyncpg://{self.postgres_app_user}:{self.postgres_app_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_master_db}"
        )

    def tenant_database_url(self, database_name: str) -> str:
        """URL de conexão ao banco de um tenant específico usando a role de aplicação."""

        return (
            f"postgresql+asyncpg://{self.postgres_app_user}:{self.postgres_app_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{database_name}"
        )


@lru_cache
def get_settings() -> Settings:
    """Retorna a instância única (cacheada) de `Settings`."""

    return Settings()
