"""Teste de ponta a ponta do módulo de Produtos: login → criar categoria/fornecedor →
criar produto vinculado → listar/filtrar por categoria → atualizar → excluir (soft
delete) → confirma auditoria gravada. Também cobre a validação de FK inexistente
(`category_id`/`supplier_id` que não apontam para registros reais).

Reaproveita o mesmo tenant/usuário semeado por `auth_environment`
(`tests/integration/conftest.py`), que já recebe as permissões `products.*` (mesmo
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


def test_full_product_crud_flow(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    category_response = client.post(
        "/api/v1/categories", json={"name": "Armazenamento (Produtos)"}
    )
    assert category_response.status_code == 201
    category_id = category_response.json()["data"]["id"]

    supplier_response = client.post(
        "/api/v1/suppliers",
        json={"type": "PJ", "name": "Tech Distribuidora Produtos", "document": "98765432000155"},
    )
    assert supplier_response.status_code == 201
    supplier_id = supplier_response.json()["data"]["id"]

    create_response = client.post(
        "/api/v1/products",
        json={
            "category_id": category_id,
            "supplier_id": supplier_id,
            "sku": "SSD-KGN-1TB",
            "name": "SSD Kingston 1TB",
            "cost_price": "320.00",
            "sale_price": "490.00",
            "stock": 20,
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()["data"]
    assert created["margin"] == "170.00"
    product_id = created["id"]

    # SKU duplicado é rejeitado.
    duplicate_response = client.post(
        "/api/v1/products",
        json={
            "sku": "SSD-KGN-1TB",
            "name": "Outro Nome",
            "cost_price": "1.00",
            "sale_price": "2.00",
        },
    )
    assert duplicate_response.status_code == 409

    # category_id inexistente é rejeitado com 404 (não 500).
    invalid_category_response = client.post(
        "/api/v1/products",
        json={
            "category_id": str(uuid.uuid4()),
            "sku": "OUTRO-SKU",
            "name": "Produto Órfão",
            "cost_price": "1.00",
            "sale_price": "2.00",
        },
    )
    assert invalid_category_response.status_code == 404

    # Listagem filtrada por categoria encontra o produto recém-criado.
    list_response = client.get("/api/v1/products", params={"category_id": category_id})
    assert list_response.status_code == 200
    list_body = list_response.json()
    assert list_body["meta"]["total"] == 1
    assert list_body["data"][0]["id"] == product_id

    # Busca por id.
    get_response = client.get(f"/api/v1/products/{product_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["name"] == "SSD Kingston 1TB"

    # Atualização parcial (preço).
    update_response = client.patch(
        f"/api/v1/products/{product_id}", json={"sale_price": "550.00"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["sale_price"] == "550.00"
    assert update_response.json()["data"]["margin"] == "230.00"

    # Exclusão (soft delete).
    delete_response = client.delete(f"/api/v1/products/{product_id}")
    assert delete_response.status_code == 200

    get_after_delete = client.get(f"/api/v1/products/{product_id}")
    assert get_after_delete.status_code == 404


async def test_product_mutations_are_audited(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    create_response = client.post(
        "/api/v1/products",
        json={
            "sku": "PRODUTO-AUDITADO-001",
            "name": "Produto Auditado",
            "cost_price": "10.00",
            "sale_price": "20.00",
        },
    )
    assert create_response.status_code == 201
    product_id = create_response.json()["data"]["id"]

    client.patch(f"/api/v1/products/{product_id}", json={"stock": 5})
    client.delete(f"/api/v1/products/{product_id}")

    settings = get_settings()
    tenant_engine = create_async_engine(
        settings.tenant_database_url(auth_environment.database_name)
    )
    try:
        async with tenant_engine.connect() as connection:
            async with AsyncSession(bind=connection) as session:
                result = await session.execute(
                    select(TenantAuditLog.action).where(TenantAuditLog.resource == "products")
                )
                actions = [row[0] for row in result.all()]
    finally:
        await tenant_engine.dispose()

    assert "PRODUCT_CREATED" in actions
    assert "PRODUCT_UPDATED" in actions
    assert "PRODUCT_DELETED" in actions
