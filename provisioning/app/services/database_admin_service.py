"""Operações administrativas de PostgreSQL (CREATE DATABASE / DROP DATABASE / Alembic).

Único ponto do sistema autorizado a executar essas operações, conforme
19-PROVISIONING-SERVICE.md e 29-SECURITY.md. Nunca reutilizado por outro serviço."""

from __future__ import annotations

import re
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from app.core.database import get_maintenance_engine, get_master_engine

_VALID_DATABASE_NAME = re.compile(r"^[a-z][a-z0-9_]{2,62}$")
_PROVISIONING_ROOT = Path(__file__).resolve().parents[2]


class DatabaseAdminService:
    """Encapsula todo comando administrativo de banco. Nomes de banco são sempre
    validados contra uma allowlist antes de compor SQL — identificadores de banco não
    podem ser parametrizados via bind params, então a validação é a única defesa."""

    def __init__(self) -> None:
        self._settings = get_settings()

    async def create_database(self, database_name: str) -> None:
        self._assert_valid_name(database_name)
        engine = get_maintenance_engine()
        async with engine.connect() as connection:
            await connection.execute(text(f'CREATE DATABASE "{database_name}"'))

    async def drop_database(self, database_name: str) -> None:
        self._assert_valid_name(database_name)
        engine = get_maintenance_engine()
        async with engine.connect() as connection:
            await connection.execute(
                text(f'DROP DATABASE IF EXISTS "{database_name}" WITH (FORCE)')
            )

    def run_tenant_migrations(self, database_name: str) -> None:
        """Executa `alembic upgrade head` contra o banco recém-criado do tenant.

        Função síncrona (Alembic é síncrono por natureza) — deve ser chamada com
        `asyncio.to_thread` a partir de um contexto assíncrono, para não colidir com o
        `asyncio.run()` interno do `env.py` do Alembic."""

        self._assert_valid_name(database_name)
        config = self._build_alembic_config("alembic_tenant")
        config.attributes["sqlalchemy_url"] = self._settings.tenant_database_url(database_name)
        command.upgrade(config, "head")

    def run_master_migrations(self) -> None:
        """Executa `alembic upgrade head` contra o Banco Master. Usado apenas pelo
        script `scripts/migrate_master.py`, fora do ciclo de requisição HTTP."""

        config = self._build_alembic_config("alembic_master")
        config.attributes["sqlalchemy_url"] = self._settings.database_master_url
        command.upgrade(config, "head")

    async def grant_app_role_privileges(self, database_name: str) -> None:
        """Concede à role `veloai_app` (usada exclusivamente pelo Backend) os
        privilégios mínimos no banco recém-criado do tenant. O Backend nunca autentica
        como a role administrativa (29-SECURITY.md)."""

        self._assert_valid_name(database_name)
        app_role = self._settings.postgres_app_user

        maintenance_engine = get_maintenance_engine()
        async with maintenance_engine.connect() as connection:
            await connection.execute(
                text(f'GRANT CONNECT ON DATABASE "{database_name}" TO "{app_role}"')
            )

        tenant_engine = create_async_engine(self._settings.tenant_database_url(database_name))
        try:
            async with tenant_engine.connect() as connection:
                await connection.execute(text(f'GRANT USAGE ON SCHEMA public TO "{app_role}"'))
                await connection.execute(
                    text(
                        "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public "
                        f'TO "{app_role}"'
                    )
                )
                await connection.execute(
                    text(
                        "ALTER DEFAULT PRIVILEGES IN SCHEMA public "
                        f'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "{app_role}"'
                    )
                )
                await connection.commit()
        finally:
            await tenant_engine.dispose()

    async def grant_app_role_privileges_on_master(self) -> None:
        """Concede à role `veloai_app` os privilégios mínimos no Banco Master (tabelas
        de leitura para roteamento de login, ex. `tenant_user_index`). Idempotente —
        chamado uma vez após `run_master_migrations()`."""

        app_role = self._settings.postgres_app_user

        maintenance_engine = get_maintenance_engine()
        async with maintenance_engine.connect() as connection:
            await connection.execute(
                text(
                    f'GRANT CONNECT ON DATABASE "{self._settings.postgres_master_db}" '
                    f'TO "{app_role}"'
                )
            )

        master_engine = get_master_engine()
        async with master_engine.connect() as connection:
            await connection.execute(text(f'GRANT USAGE ON SCHEMA public TO "{app_role}"'))
            await connection.execute(
                text(
                    "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public "
                    f'TO "{app_role}"'
                )
            )
            await connection.execute(
                text(
                    "ALTER DEFAULT PRIVILEGES IN SCHEMA public "
                    f'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "{app_role}"'
                )
            )
            await connection.commit()

    @staticmethod
    def _build_alembic_config(section: str) -> Config:
        ini_path = _PROVISIONING_ROOT / f"{section}.ini"
        config = Config(str(ini_path))
        config.set_main_option("script_location", str(_PROVISIONING_ROOT / section))
        return config

    @staticmethod
    def _assert_valid_name(database_name: str) -> None:
        if not _VALID_DATABASE_NAME.match(database_name):
            raise ValueError(f"Nome de banco inválido: {database_name!r}")
