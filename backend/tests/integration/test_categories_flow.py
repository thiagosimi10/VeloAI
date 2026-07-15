"""Teste de ponta a ponta do módulo de Categorias: login → criar → listar/buscar →
buscar por id → atualizar → excluir (soft delete) → confirma auditoria gravada.

Reaproveita o mesmo tenant/usuário semeado por `auth_environment`
(`tests/integration/conftest.py`), que já recebe as permissões `categories.*` (mesmo
catálogo usado pelo seed real do Provisioning)."""

from __future__ import annotations

from fakeredis import aioredis as fakeredis_aioredis
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from veloai_shared.schema.tenant import TenantAuditLog

from app.core.config import get_settings
from app.core.rate_limit import LoginRateLimiter, get_login_rate_limiter
from app.main import app

from .conftest import AuthFixtureData

app.dependency_overrides[get_login_rate_limiter] = lambda: LoginRateLimiter(
    fakeredis_aioredis.FakeRedis(decode_responses=True)
)


def _login(client: TestClient, fixture: AuthFixtureData, password: str) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": fixture.user_email, "password": password},
    )
    assert response.status_code == 200


def test_full_category_crud_flow(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    create_response = client.post(
        "/api/v1/categories",
        json={"name": "Armazenamento de Teste", "description": "SSDs e HDs"},
    )
    assert create_response.status_code == 201
    created = create_response.json()["data"]
    assert created["name"] == "Armazenamento de Teste"
    category_id = created["id"]

    # Nome duplicado é rejeitado.
    duplicate_response = client.post(
        "/api/v1/categories", json={"name": "Armazenamento de Teste"}
    )
    assert duplicate_response.status_code == 409

    # Listagem com busca encontra a categoria recém-criada.
    list_response = client.get(
        "/api/v1/categories", params={"search": "Armazenamento de Teste"}
    )
    assert list_response.status_code == 200
    list_body = list_response.json()
    assert list_body["meta"]["total"] == 1
    assert list_body["data"][0]["id"] == category_id

    # Busca por id.
    get_response = client.get(f"/api/v1/categories/{category_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["name"] == "Armazenamento de Teste"

    # Atualização parcial.
    update_response = client.patch(
        f"/api/v1/categories/{category_id}", json={"description": "Nova descrição"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["description"] == "Nova descrição"

    # Exclusão (soft delete).
    delete_response = client.delete(f"/api/v1/categories/{category_id}")
    assert delete_response.status_code == 200

    get_after_delete = client.get(f"/api/v1/categories/{category_id}")
    assert get_after_delete.status_code == 404


async def test_category_mutations_are_audited(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    create_response = client.post(
        "/api/v1/categories", json={"name": "Categoria Auditada"}
    )
    assert create_response.status_code == 201
    category_id = create_response.json()["data"]["id"]

    client.patch(f"/api/v1/categories/{category_id}", json={"description": "observação"})
    client.delete(f"/api/v1/categories/{category_id}")

    settings = get_settings()
    tenant_engine = create_async_engine(
        settings.tenant_database_url(auth_environment.database_name)
    )
    try:
        async with tenant_engine.connect() as connection:
            async with AsyncSession(bind=connection) as session:
                result = await session.execute(
                    select(TenantAuditLog.action).where(TenantAuditLog.resource == "categories")
                )
                actions = [row[0] for row in result.all()]
    finally:
        await tenant_engine.dispose()

    assert "CATEGORY_CREATED" in actions
    assert "CATEGORY_UPDATED" in actions
    assert "CATEGORY_DELETED" in actions
