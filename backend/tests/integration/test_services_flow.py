"""Teste de ponta a ponta do módulo de Serviços: login → criar categoria → criar serviço
vinculado → listar/filtrar por categoria → atualizar → excluir (soft delete) → confirma
auditoria gravada. Também cobre a validação de FK inexistente (`category_id` que não
aponta para um registro real).

Reaproveita o mesmo tenant/usuário semeado por `auth_environment`
(`tests/integration/conftest.py`), que já recebe as permissões `services.*` (mesmo
catálogo usado pelo seed real do Provisioning)."""

from __future__ import annotations

import uuid

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


def test_full_service_crud_flow(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    category_response = client.post(
        "/api/v1/categories", json={"name": "Manutenção (Serviços)"}
    )
    assert category_response.status_code == 201
    category_id = category_response.json()["data"]["id"]

    create_response = client.post(
        "/api/v1/services",
        json={
            "category_id": category_id,
            "name": "Formatação de Computador",
            "price": "180.00",
            "estimated_time": 60,
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()["data"]
    assert created["code"] == "S000001"
    service_id = created["id"]

    # category_id inexistente é rejeitado com 404 (não 500).
    invalid_category_response = client.post(
        "/api/v1/services",
        json={
            "category_id": str(uuid.uuid4()),
            "name": "Serviço Órfão",
            "price": "50.00",
        },
    )
    assert invalid_category_response.status_code == 404

    # Listagem filtrada por categoria encontra o serviço recém-criado.
    list_response = client.get("/api/v1/services", params={"category_id": category_id})
    assert list_response.status_code == 200
    list_body = list_response.json()
    assert list_body["meta"]["total"] == 1
    assert list_body["data"][0]["id"] == service_id

    # Busca por id.
    get_response = client.get(f"/api/v1/services/{service_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["name"] == "Formatação de Computador"

    # Atualização parcial (preço).
    update_response = client.patch(
        f"/api/v1/services/{service_id}", json={"price": "220.00"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["price"] == "220.00"

    # Exclusão (soft delete).
    delete_response = client.delete(f"/api/v1/services/{service_id}")
    assert delete_response.status_code == 200

    get_after_delete = client.get(f"/api/v1/services/{service_id}")
    assert get_after_delete.status_code == 404


async def test_service_mutations_are_audited(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    create_response = client.post(
        "/api/v1/services", json={"name": "Serviço Auditado", "price": "99.00"}
    )
    assert create_response.status_code == 201
    service_id = create_response.json()["data"]["id"]
    # Regressão: `test_full_service_crud_flow` já criou e excluiu (soft delete) um
    # serviço com código "S000001" neste mesmo tenant. A geração do próximo código
    # precisa considerar também os registros excluídos (código é único na tabela
    # inteira) — do contrário, este INSERT falharia com violação de unicidade.
    assert create_response.json()["data"]["code"] != "S000001"

    client.patch(f"/api/v1/services/{service_id}", json={"description": "observação"})
    client.delete(f"/api/v1/services/{service_id}")

    settings = get_settings()
    tenant_engine = create_async_engine(
        settings.tenant_database_url(auth_environment.database_name)
    )
    try:
        async with tenant_engine.connect() as connection:
            async with AsyncSession(bind=connection) as session:
                result = await session.execute(
                    select(TenantAuditLog.action).where(TenantAuditLog.resource == "services")
                )
                actions = [row[0] for row in result.all()]
    finally:
        await tenant_engine.dispose()

    assert "SERVICE_CREATED" in actions
    assert "SERVICE_UPDATED" in actions
    assert "SERVICE_DELETED" in actions
