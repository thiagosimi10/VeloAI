"""Ambiente Alembic assíncrono para o Banco Master (`veloai_master`).

Segue o padrão assíncrono oficial do Alembic (asyncio + `run_sync`) para reutilizar o
mesmo driver `asyncpg` usado pela aplicação, sem exigir um segundo driver síncrono."""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from veloai_shared.schema.master import MasterBase

from app.core.config import get_settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = MasterBase.metadata


def get_url() -> str:
    """Prioriza a URL passada programaticamente via `config.attributes` (usada pelo
    `DatabaseAdminService`); cai para `Settings` como padrão para uso via CLI."""

    return config.attributes.get("sqlalchemy_url") or get_settings().database_master_url


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration, prefix="sqlalchemy.", poolclass=pool.NullPool
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
