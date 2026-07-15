"""Teste de ponta a ponta do módulo de Ordens de Serviço (Fase 8 — núcleo operacional):
login → criar cliente/produto/serviço → criar OS → adicionar item de produto e de
serviço → iniciar → concluir sem técnico falha → concluir com técnico → confere que o
estoque do produto baixou automaticamente e que o histórico registra o consumo →
remover item após concluída falha → cancelar uma segunda OS → auditoria gravada.

Reaproveita o mesmo tenant/usuário semeado por `auth_environment`
(`tests/integration/conftest.py`), que já recebe as permissões `service_orders.*`/
`users.view` (mesmo catálogo usado pelo seed real do Provisioning)."""

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


def _login(client: TestClient, fixture: AuthFixtureData, password: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": fixture.user_email, "password": password},
    )
    assert response.status_code == 200

    me_response = client.get("/api/v1/auth/me")
    assert me_response.status_code == 200
    return me_response.json()["data"]["id"]


def test_full_service_order_flow(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    technician_id = _login(client, auth_environment, auth_environment.temporary_password)

    customer_response = client.post(
        "/api/v1/customers",
        json={"type": "PF", "name": "Cliente OS", "document": "111.444.777-35"},
    )
    assert customer_response.status_code == 201
    customer_id = customer_response.json()["data"]["id"]

    product_response = client.post(
        "/api/v1/products",
        json={
            "sku": "SSD-OS-001",
            "name": "SSD para Teste de OS",
            "cost_price": "320.00",
            "sale_price": "490.00",
            "stock": 10,
        },
    )
    assert product_response.status_code == 201
    product_id = product_response.json()["data"]["id"]

    service_response = client.post(
        "/api/v1/services", json={"name": "Formatação de Computador", "price": "180.00"}
    )
    assert service_response.status_code == 201
    service_id = service_response.json()["data"]["id"]

    # Cria a OS.
    create_response = client.post(
        "/api/v1/service-orders",
        json={"customer_id": customer_id, "equipment": "Notebook Dell", "problem": "Não liga"},
    )
    assert create_response.status_code == 201
    order = create_response.json()["data"]
    assert order["number"].startswith("OS-")
    assert order["status"] == "open"
    order_id = order["id"]

    # Adiciona um item de produto (sem unit_price — herda o preço de catálogo).
    product_item_response = client.post(
        f"/api/v1/service-orders/{order_id}/items",
        json={"product_id": product_id, "quantity": 2},
    )
    assert product_item_response.status_code == 201
    product_item = product_item_response.json()["data"]
    assert product_item["unit_price"] == "490.00"
    assert product_item["total"] == "980.00"

    # Adiciona um item de serviço.
    service_item_response = client.post(
        f"/api/v1/service-orders/{order_id}/items",
        json={"service_id": service_id, "quantity": 1},
    )
    assert service_item_response.status_code == 201

    get_response = client.get(f"/api/v1/service-orders/{order_id}")
    assert get_response.status_code == 200
    order_detail = get_response.json()["data"]
    assert len(order_detail["items"]) == 2
    assert order_detail["total"] == "1160.00"

    # Inicia o atendimento.
    start_response = client.post(f"/api/v1/service-orders/{order_id}/start")
    assert start_response.status_code == 200
    assert start_response.json()["data"]["status"] == "in_progress"

    # Concluir sem técnico responsável falha.
    close_without_technician = client.post(f"/api/v1/service-orders/{order_id}/close", json={})
    assert close_without_technician.status_code == 422

    # Concluir informando o técnico dá certo, consome o estoque do item de produto.
    close_response = client.post(
        f"/api/v1/service-orders/{order_id}/close",
        json={"technician_id": technician_id},
    )
    assert close_response.status_code == 200
    closed_order = close_response.json()["data"]
    assert closed_order["status"] == "completed"
    assert closed_order["finished_at"] is not None
    assert closed_order["technician_id"] == technician_id

    product_after_close = client.get(f"/api/v1/products/{product_id}")
    assert product_after_close.json()["data"]["stock"] == 8

    stock_history = client.get(f"/api/v1/products/{product_id}/stock-movements")
    assert stock_history.json()["meta"]["total"] == 1
    assert order["number"] in stock_history.json()["data"][0]["reason"]

    # Não é possível remover item de uma OS concluída.
    item_id = product_item["id"]
    remove_after_close = client.delete(
        f"/api/v1/service-orders/{order_id}/items/{item_id}"
    )
    assert remove_after_close.status_code == 422

    # Segunda OS: cancelamento.
    second_order_response = client.post(
        "/api/v1/service-orders", json={"customer_id": customer_id}
    )
    second_order_id = second_order_response.json()["data"]["id"]
    cancel_response = client.post(f"/api/v1/service-orders/{second_order_id}/cancel")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["data"]["status"] == "cancelled"


def test_close_service_order_rejects_insufficient_stock(
    auth_environment: AuthFixtureData,
) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    customer_response = client.post(
        "/api/v1/customers",
        json={"type": "PF", "name": "Cliente Estoque Insuficiente", "document": "98765432100"},
    )
    customer_id = customer_response.json()["data"]["id"]

    product_response = client.post(
        "/api/v1/products",
        json={
            "sku": "SSD-OS-002",
            "name": "SSD com Pouco Estoque",
            "cost_price": "100.00",
            "sale_price": "150.00",
            "stock": 1,
        },
    )
    product_id = product_response.json()["data"]["id"]

    order_response = client.post("/api/v1/service-orders", json={"customer_id": customer_id})
    order_id = order_response.json()["data"]["id"]

    client.post(
        f"/api/v1/service-orders/{order_id}/items",
        json={"product_id": product_id, "quantity": 5},
    )
    client.post(f"/api/v1/service-orders/{order_id}/start")

    me_response = client.get("/api/v1/auth/me")
    technician_id = me_response.json()["data"]["id"]

    close_response = client.post(
        f"/api/v1/service-orders/{order_id}/close",
        json={"technician_id": technician_id},
    )
    assert close_response.status_code == 409

    # O estoque não foi alterado pela tentativa rejeitada.
    product_after_failed_close = client.get(f"/api/v1/products/{product_id}")
    assert product_after_failed_close.json()["data"]["stock"] == 1


async def test_service_order_lifecycle_is_audited(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    customer_response = client.post(
        "/api/v1/customers",
        json={"type": "PF", "name": "Cliente Auditado", "document": "12345678909"},
    )
    customer_id = customer_response.json()["data"]["id"]

    order_response = client.post("/api/v1/service-orders", json={"customer_id": customer_id})
    order_id = order_response.json()["data"]["id"]
    client.post(f"/api/v1/service-orders/{order_id}/start")
    client.post(f"/api/v1/service-orders/{order_id}/cancel")

    settings = get_settings()
    tenant_engine = create_async_engine(
        settings.tenant_database_url(auth_environment.database_name)
    )
    try:
        async with tenant_engine.connect() as connection:
            async with AsyncSession(bind=connection) as session:
                result = await session.execute(
                    select(TenantAuditLog.action).where(
                        TenantAuditLog.resource == "service_orders"
                    )
                )
                actions = [row[0] for row in result.all()]
    finally:
        await tenant_engine.dispose()

    assert "SERVICE_ORDER_CREATED" in actions
    assert "SERVICE_ORDER_STARTED" in actions
    assert "SERVICE_ORDER_CANCELLED" in actions
