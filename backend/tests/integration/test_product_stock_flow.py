"""Teste de ponta a ponta do ajuste de estoque de Produtos (Fase 7 — Estoque): login →
criar produto com estoque inicial → registrar entrada → registrar saída → conferir que
`GET /products/{id}` reflete o novo estoque → listar histórico → saída maior que o
disponível retorna 409 (não 500) → confirma auditoria gravada.

Reaproveita o mesmo tenant/usuário semeado por `auth_environment`
(`tests/integration/conftest.py`), que já recebe as permissões `stock.*` (mesmo
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


def test_full_product_stock_adjustment_flow(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    create_response = client.post(
        "/api/v1/products",
        json={
            "sku": "SSD-ESTOQUE-001",
            "name": "SSD para Teste de Estoque",
            "cost_price": "320.00",
            "sale_price": "490.00",
            "stock": 10,
        },
    )
    assert create_response.status_code == 201
    product_id = create_response.json()["data"]["id"]

    # Entrada de 5 unidades: 10 -> 15.
    in_response = client.post(
        f"/api/v1/products/{product_id}/stock-movements",
        json={"movement": "in", "quantity": 5, "reason": "Compra de reposição"},
    )
    assert in_response.status_code == 201
    assert in_response.json()["data"]["previous_stock"] == 10
    assert in_response.json()["data"]["current_stock"] == 15

    # Saída de 3 unidades: 15 -> 12.
    out_response = client.post(
        f"/api/v1/products/{product_id}/stock-movements",
        json={"movement": "out", "quantity": 3, "reason": "Venda balcão"},
    )
    assert out_response.status_code == 201
    assert out_response.json()["data"]["current_stock"] == 12

    # O produto reflete o novo estoque.
    get_response = client.get(f"/api/v1/products/{product_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["stock"] == 12

    # Histórico lista as duas movimentações, mais recente primeiro.
    history_response = client.get(f"/api/v1/products/{product_id}/stock-movements")
    assert history_response.status_code == 200
    history_body = history_response.json()
    assert history_body["meta"]["total"] == 2
    assert history_body["data"][0]["movement"] == "out"
    assert history_body["data"][1]["movement"] == "in"

    # Saída maior que o disponível é rejeitada com 409 (não 500 nem estoque negativo).
    insufficient_response = client.post(
        f"/api/v1/products/{product_id}/stock-movements",
        json={"movement": "out", "quantity": 999, "reason": "Venda balcão"},
    )
    assert insufficient_response.status_code == 409

    # O estoque não foi alterado pela tentativa rejeitada.
    get_after_rejection = client.get(f"/api/v1/products/{product_id}")
    assert get_after_rejection.json()["data"]["stock"] == 12

    # Ajuste de inventário define o valor absoluto: vira 50 independente do estoque atual.
    adjustment_response = client.post(
        f"/api/v1/products/{product_id}/stock-movements",
        json={"movement": "adjustment", "quantity": 50, "reason": "Contagem de inventário"},
    )
    assert adjustment_response.status_code == 201
    assert adjustment_response.json()["data"]["current_stock"] == 50


async def test_stock_adjustment_is_audited(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    create_response = client.post(
        "/api/v1/products",
        json={
            "sku": "SSD-ESTOQUE-AUDITADO-001",
            "name": "SSD Auditado",
            "cost_price": "100.00",
            "sale_price": "150.00",
            "stock": 5,
        },
    )
    assert create_response.status_code == 201
    product_id = create_response.json()["data"]["id"]

    client.post(
        f"/api/v1/products/{product_id}/stock-movements",
        json={"movement": "in", "quantity": 2, "reason": "Compra de reposição"},
    )

    settings = get_settings()
    tenant_engine = create_async_engine(
        settings.tenant_database_url(auth_environment.database_name)
    )
    try:
        async with tenant_engine.connect() as connection:
            async with AsyncSession(bind=connection) as session:
                result = await session.execute(
                    select(TenantAuditLog.action).where(
                        TenantAuditLog.resource == "products",
                        TenantAuditLog.action == "PRODUCT_STOCK_ADJUSTED",
                    )
                )
                actions = [row[0] for row in result.all()]
    finally:
        await tenant_engine.dispose()

    assert "PRODUCT_STOCK_ADJUSTED" in actions
