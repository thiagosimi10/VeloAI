"""Teste de ponta a ponta do módulo de Clientes: login → criar → listar/buscar →
buscar por id → atualizar → excluir (soft delete) → confirma auditoria gravada.

Reaproveita o mesmo tenant/usuário semeado por `auth_environment`
(`tests/integration/conftest.py`), que já recebe as permissões `customers.*` (mesmo
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


def test_full_customer_crud_flow(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    create_response = client.post(
        "/api/v1/customers",
        json={
            "type": "PF",
            "name": "Cliente de Teste",
            "document": "111.444.777-35",
            "email": "cliente@teste.test",
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()["data"]
    assert created["code"] == "C000001"
    assert created["document"] == "11144477735"
    customer_id = created["id"]

    # Documento duplicado é rejeitado.
    duplicate_response = client.post(
        "/api/v1/customers",
        json={"type": "PF", "name": "Outro Nome", "document": "111.444.777-35"},
    )
    assert duplicate_response.status_code == 409

    # Listagem com busca encontra o cliente recém-criado.
    list_response = client.get("/api/v1/customers", params={"search": "Cliente de Teste"})
    assert list_response.status_code == 200
    list_body = list_response.json()
    assert list_body["meta"]["total"] == 1
    assert list_body["data"][0]["id"] == customer_id

    # Busca por id.
    get_response = client.get(f"/api/v1/customers/{customer_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["name"] == "Cliente de Teste"

    # Atualização parcial.
    update_response = client.patch(
        f"/api/v1/customers/{customer_id}", json={"phone": "19999999999"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["phone"] == "19999999999"
    assert update_response.json()["data"]["name"] == "Cliente de Teste"

    # Exclusão (soft delete).
    delete_response = client.delete(f"/api/v1/customers/{customer_id}")
    assert delete_response.status_code == 200

    get_after_delete = client.get(f"/api/v1/customers/{customer_id}")
    assert get_after_delete.status_code == 404

    list_after_delete = client.get("/api/v1/customers")
    assert list_after_delete.json()["meta"]["total"] == 0


async def test_customer_mutations_are_audited(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    create_response = client.post(
        "/api/v1/customers",
        json={"type": "PJ", "name": "Empresa Auditada LTDA", "document": "12.345.678/0001-99"},
    )
    assert create_response.status_code == 201
    customer_id = create_response.json()["data"]["id"]
    # Regressão: `test_full_customer_crud_flow` já criou e excluiu (soft delete) um
    # cliente com código "C000001" neste mesmo tenant. A geração do próximo código
    # precisa considerar também os registros excluídos (código é único na tabela
    # inteira) — do contrário, este INSERT falharia com violação de unicidade.
    assert create_response.json()["data"]["code"] != "C000001"

    client.patch(f"/api/v1/customers/{customer_id}", json={"notes": "observação"})
    client.delete(f"/api/v1/customers/{customer_id}")

    settings = get_settings()
    tenant_engine = create_async_engine(
        settings.tenant_database_url(auth_environment.database_name)
    )
    try:
        async with tenant_engine.connect() as connection:
            async with AsyncSession(bind=connection) as session:
                result = await session.execute(
                    select(TenantAuditLog.action).where(TenantAuditLog.resource == "customers")
                )
                actions = [row[0] for row in result.all()]
    finally:
        await tenant_engine.dispose()

    assert "CUSTOMER_CREATED" in actions
    assert "CUSTOMER_UPDATED" in actions
    assert "CUSTOMER_DELETED" in actions
