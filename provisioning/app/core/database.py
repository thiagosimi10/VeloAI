"""Fábricas de engine/sessão para o Banco Master e para a conexão de manutenção usada
exclusivamente em `CREATE DATABASE` / `DROP DATABASE` (19-PROVISIONING-SERVICE.md,
29-SECURITY.md: "Somente o Provisioning Service poderá possuir CREATE DATABASE, DROP
DATABASE, CREATE USER, ALTER DATABASE, CREATE SCHEMA.")."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings


@lru_cache
def get_master_engine() -> AsyncEngine:
    """Engine com pool reutilizável para o Banco Master (`veloai_master`)."""

    settings = get_settings()
    return create_async_engine(settings.database_master_url, pool_pre_ping=True)


@lru_cache
def get_maintenance_engine() -> AsyncEngine:
    """Engine em modo AUTOCOMMIT conectado à base de manutenção (`postgres`). `CREATE
    DATABASE`/`DROP DATABASE` não podem ser executados dentro de uma transação."""

    settings = get_settings()
    return create_async_engine(settings.maintenance_database_url, isolation_level="AUTOCOMMIT")


def get_master_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=get_master_engine(), expire_on_commit=False)


@asynccontextmanager
async def get_master_session() -> AsyncIterator[AsyncSession]:
    session_factory = get_master_sessionmaker()
    async with session_factory() as session:
        yield session


async def dispose_engines() -> None:
    """Fecha os pools de conexão. Chamado no shutdown da aplicação e ao final dos testes."""

    await get_master_engine().dispose()
    await get_maintenance_engine().dispose()
