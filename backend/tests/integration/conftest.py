"""Fixtures de integração do Backend — fluxo real de autenticação.

Diferente do Provisioning Service, o Backend nunca cria bancos em produção. Para testar
`TenantConnectionManager`/`LoginUseCase` de ponta a ponta, esta suíte monta o cenário
diretamente (banco master + banco de tenant + role `veloai_app`) usando uma conexão de
superusuário disponível apenas em ambiente de teste — o código do Backend sob teste
continua usando exclusivamente a role `veloai_app`, nunca a de superusuário.

Exige um PostgreSQL e um Redis reais (fornecidos como service containers no CI — ver
`.github/workflows/backend-ci.yml`). Se indisponíveis, os testes são pulados."""

from __future__ import annotations

import os

# As variáveis de ambiente precisam existir ANTES de qualquer módulo do Backend ser
# importado (em particular `app.main`, que resolve `Settings` uma única vez na
# importação) — por isso são definidas aqui, no nível do módulo do conftest, que o
# pytest sempre importa antes dos arquivos de teste do mesmo diretório.
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ["POSTGRES_MASTER_DB"] = "veloai_master_auth_test"
os.environ["POSTGRES_APP_USER"] = "veloai_app"
os.environ["POSTGRES_APP_PASSWORD"] = "app-role-test-password"  # noqa: S105 - segredo de teste
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET", "integration-test-jwt-secret")
os.environ.setdefault("JWT_REFRESH_SECRET", "integration-test-jwt-refresh-secret")

import uuid  # noqa: E402
from collections.abc import AsyncIterator  # noqa: E402
from dataclasses import dataclass  # noqa: E402

import asyncpg  # noqa: E402
import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import create_async_engine  # noqa: E402
from veloai_shared.permissions_catalog import DEFAULT_ADMIN_PERMISSIONS  # noqa: E402
from veloai_shared.schema.master import MasterBase, Tenant, TenantStatus, TenantUserIndex  # noqa: E402
from veloai_shared.schema.tenant import (  # noqa: E402
    Company,
    TenantBase,
    TenantPermission,
    TenantRole,
    TenantRolePermission,
    TenantUser,
)
from veloai_shared.security import hash_password, new_uuid7  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.database import get_master_engine, get_tenant_connection_manager  # noqa: E402
from app.core.rate_limit import get_redis_client  # noqa: E402

MASTER_DB = "veloai_master_auth_test"
TENANT_DB = "tenant_auth_test"
ADMIN_USER = "postgres"
ADMIN_PASSWORD = "postgres"

TEST_USER_EMAIL = "maria@assistenciasilva.test"
TEST_USER_TEMP_PASSWORD = "Temp0rary!Pass"  # noqa: S105 - segredo de teste


@dataclass(frozen=True)
class AuthFixtureData:
    tenant_id: uuid.UUID
    database_name: str
    user_email: str
    temporary_password: str


def _admin_url(database: str) -> str:
    host = os.environ["POSTGRES_HOST"]
    port = os.environ["POSTGRES_PORT"]
    return f"postgresql+asyncpg://{ADMIN_USER}:{ADMIN_PASSWORD}@{host}:{port}/{database}"


async def _postgres_available() -> bool:
    try:
        connection = await asyncpg.connect(
            host=os.environ["POSTGRES_HOST"],
            port=int(os.environ["POSTGRES_PORT"]),
            user=ADMIN_USER,
            password=ADMIN_PASSWORD,
            database="postgres",
            timeout=2,
        )
    except Exception:  # noqa: BLE001 - qualquer falha de conexão apenas pula os testes
        return False
    await connection.close()
    return True


async def _drop_database(database: str) -> None:
    connection = await asyncpg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        user=ADMIN_USER,
        password=ADMIN_PASSWORD,
        database="postgres",
    )
    try:
        await connection.execute(f'DROP DATABASE IF EXISTS "{database}" WITH (FORCE)')
    finally:
        await connection.close()


async def _create_database(database: str) -> None:
    connection = await asyncpg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        user=ADMIN_USER,
        password=ADMIN_PASSWORD,
        database="postgres",
    )
    try:
        await connection.execute(f'CREATE DATABASE "{database}"')
    finally:
        await connection.close()


async def _ensure_app_role_exists() -> None:
    connection = await asyncpg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        user=ADMIN_USER,
        password=ADMIN_PASSWORD,
        database="postgres",
    )
    try:
        role_name = os.environ["POSTGRES_APP_USER"]
        password = os.environ["POSTGRES_APP_PASSWORD"]
        await connection.execute(
            f"""
            DO $do$
            BEGIN
                IF NOT EXISTS (
                    SELECT FROM pg_catalog.pg_roles WHERE rolname = '{role_name}'
                ) THEN
                    CREATE ROLE "{role_name}" LOGIN PASSWORD
                        '{password}' NOCREATEDB NOCREATEROLE NOSUPERUSER;
                END IF;
            END
            $do$;
            """
        )
        await connection.execute(f'GRANT CONNECT ON DATABASE "{MASTER_DB}" TO "{role_name}"')
        await connection.execute(f'GRANT CONNECT ON DATABASE "{TENANT_DB}" TO "{role_name}"')
    finally:
        await connection.close()


async def _grant_app_privileges(database: str) -> None:
    role_name = os.environ["POSTGRES_APP_USER"]
    engine = create_async_engine(_admin_url(database))
    try:
        async with engine.begin() as connection:
            await connection.execute(text(f'GRANT USAGE ON SCHEMA public TO "{role_name}"'))
            await connection.execute(
                text(
                    "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public "
                    f'TO "{role_name}"'
                )
            )
    finally:
        await engine.dispose()


async def _create_schema(database: str, metadata_owner: type) -> None:
    engine = create_async_engine(_admin_url(database))
    try:
        async with engine.begin() as connection:
            await connection.run_sync(metadata_owner.metadata.create_all)
    finally:
        await engine.dispose()


async def _seed_test_data() -> AuthFixtureData:
    tenant_id = new_uuid7()

    engine = create_async_engine(_admin_url(MASTER_DB))
    try:
        async with engine.begin() as connection:
            await connection.execute(
                Tenant.__table__.insert().values(
                    id=tenant_id,
                    legal_name="Assistência Técnica Silva LTDA",
                    document="12345678000199",
                    database_name=TENANT_DB,
                    database_host=os.environ["POSTGRES_HOST"],
                    database_port=int(os.environ["POSTGRES_PORT"]),
                    status=TenantStatus.ACTIVE.value,
                )
            )
            await connection.execute(
                TenantUserIndex.__table__.insert().values(
                    id=new_uuid7(), email=TEST_USER_EMAIL, tenant_id=tenant_id
                )
            )
    finally:
        await engine.dispose()

    tenant_engine = create_async_engine(_admin_url(TENANT_DB))
    try:
        async with tenant_engine.begin() as connection:
            company_id = new_uuid7()
            role_id = new_uuid7()
            user_id = new_uuid7()

            await connection.execute(
                Company.__table__.insert().values(
                    id=company_id,
                    legal_name="Assistência Técnica Silva LTDA",
                    document="12345678000199",
                )
            )
            await connection.execute(
                TenantRole.__table__.insert().values(id=role_id, name="Administrador")
            )
            # Mesmo catálogo usado pelo seed real do Provisioning — mantém o tenant de
            # teste fiel ao que um tenant provisionado de verdade recebe.
            for module, action in DEFAULT_ADMIN_PERMISSIONS:
                permission_id = new_uuid7()
                await connection.execute(
                    TenantPermission.__table__.insert().values(
                        id=permission_id, module=module, action=action
                    )
                )
                await connection.execute(
                    TenantRolePermission.__table__.insert().values(
                        id=new_uuid7(), role_id=role_id, permission_id=permission_id
                    )
                )
            await connection.execute(
                TenantUser.__table__.insert().values(
                    id=user_id,
                    company_id=company_id,
                    role_id=role_id,
                    first_name="Maria",
                    last_name="Souza",
                    email=TEST_USER_EMAIL,
                    password_hash=hash_password(TEST_USER_TEMP_PASSWORD),
                    active=True,
                    force_password_change=True,
                )
            )
    finally:
        await tenant_engine.dispose()

    return AuthFixtureData(
        tenant_id=tenant_id,
        database_name=TENANT_DB,
        user_email=TEST_USER_EMAIL,
        temporary_password=TEST_USER_TEMP_PASSWORD,
    )


def _clear_backend_caches() -> None:
    get_settings.cache_clear()
    get_master_engine.cache_clear()
    get_tenant_connection_manager.cache_clear()
    get_redis_client.cache_clear()


@pytest_asyncio.fixture(scope="session")
async def auth_environment() -> AsyncIterator[AuthFixtureData]:
    if not await _postgres_available():
        pytest.skip("PostgreSQL indisponível — pulando testes de integração de Autenticação.")

    _clear_backend_caches()

    await _drop_database(MASTER_DB)
    await _drop_database(TENANT_DB)
    await _create_database(MASTER_DB)
    await _create_database(TENANT_DB)
    # A role precisa existir e as bases já criadas antes do GRANT CONNECT (que referencia
    # os nomes das bases).
    await _ensure_app_role_exists()
    await _create_schema(MASTER_DB, MasterBase)
    await _create_schema(TENANT_DB, TenantBase)
    await _grant_app_privileges(MASTER_DB)
    await _grant_app_privileges(TENANT_DB)

    fixture_data = await _seed_test_data()

    _clear_backend_caches()

    yield fixture_data

    await get_master_engine().dispose()
    await get_tenant_connection_manager().dispose_all()
    await get_redis_client().aclose()
    await _drop_database(MASTER_DB)
    await _drop_database(TENANT_DB)
