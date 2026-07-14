"""Fixtures de integração do Provisioning Service.

Estes testes exigem um PostgreSQL real acessível (fornecido como service container no
CI — ver `.github/workflows/backend-ci.yml`). Quando indisponível (ex.: execução local
sem Docker), os testes de integração são pulados automaticamente em vez de falhar."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import asyncpg
import pytest
import pytest_asyncio

from app.core.config import get_settings
from app.core.database import get_maintenance_engine, get_master_engine
from app.services.database_admin_service import DatabaseAdminService

TEST_MASTER_DB = "veloai_master_test"


def _configure_test_environment() -> None:
    os.environ.setdefault("POSTGRES_HOST", "localhost")
    os.environ.setdefault("POSTGRES_PORT", "5432")
    os.environ.setdefault("POSTGRES_USER", "postgres")
    os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
    os.environ.setdefault("POSTGRES_MAINTENANCE_DB", "postgres")

    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    host = os.environ["POSTGRES_HOST"]
    port = os.environ["POSTGRES_PORT"]
    os.environ["DATABASE_MASTER_URL"] = (
        f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{TEST_MASTER_DB}"
    )
    get_settings.cache_clear()


async def _postgres_available() -> bool:
    settings = get_settings()
    try:
        connection = await asyncpg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_maintenance_db,
            timeout=2,
        )
    except Exception:  # noqa: BLE001 - qualquer falha de conexão apenas pula os testes
        return False
    await connection.close()
    return True


@pytest_asyncio.fixture(scope="session")
async def master_database() -> AsyncIterator[None]:
    _configure_test_environment()

    if not await _postgres_available():
        pytest.skip("PostgreSQL indisponível — pulando testes de integração do Provisioning.")

    admin_service = DatabaseAdminService()
    await admin_service.drop_database(TEST_MASTER_DB)
    await admin_service.create_database(TEST_MASTER_DB)
    admin_service.run_master_migrations()

    yield

    await get_master_engine().dispose()
    await get_maintenance_engine().dispose()
    await admin_service.drop_database(TEST_MASTER_DB)
