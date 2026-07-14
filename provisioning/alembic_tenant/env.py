"""Ambiente Alembic assíncrono aplicado ao banco de CADA tenant.

A URL de conexão nunca é fixa — é sempre injetada dinamicamente por
`DatabaseAdminService.run_tenant_migrations()` via `config.attributes["sqlalchemy_url"]`,
pois cada tenant possui seu próprio banco PostgreSQL."""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from app.models.tenant_template import TenantBase

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = TenantBase.metadata


def get_url() -> str:
    url = config.attributes.get("sqlalchemy_url")
    if not url:
        raise RuntimeError(
            "alembic_tenant requer 'sqlalchemy_url' em config.attributes — "
            "nunca possui uma URL fixa, pois roda contra um banco por tenant."
        )
    return url


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
