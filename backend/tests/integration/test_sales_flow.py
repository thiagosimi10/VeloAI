"""Teste de ponta a ponta do módulo de Vendas (Fase 9 — núcleo operacional): login →
criar cliente/produto → criar venda → adicionar item de produto [herda `sale_price`] →
GET reflete total e itens → aplicar desconto via `update` → `complete` → confere baixa
de estoque automática e histórico → item bloqueado após `paid` → estoque insuficiente
no `complete` retorna 409 e não altera o estoque → segunda venda cancelada →
auditoria gravada.

Reaproveita o mesmo tenant/usuário semeado por `auth_environment`
(`tests/integration/conftest.py`), que já recebe as permissões `sales.*` (mesmo
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


def test_full_sale_flow(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    customer_response = client.post(
        "/api/v1/customers",
        json={"type": "PF", "name": "Cliente Venda", "document": "111.444.777-35"},
    )
    assert customer_response.status_code == 201
    customer_id = customer_response.json()["data"]["id"]

    product_response = client.post(
        "/api/v1/products",
        json={
            "sku": "SSD-VND-001",
            "name": "SSD para Teste de Venda",
            "cost_price": "320.00",
            "sale_price": "490.00",
            "stock": 10,
        },
    )
    assert product_response.status_code == 201
    product_id = product_response.json()["data"]["id"]

    # Cria a venda.
    create_response = client.post(
        "/api/v1/sales", json={"customer_id": customer_id, "payment_method": "pix"}
    )
    assert create_response.status_code == 201
    sale = create_response.json()["data"]
    assert sale["status"] == "open"
    assert sale["payment_method"] == "pix"
    sale_id = sale["id"]

    # Adiciona um item de produto (sem unit_price — herda o preço de catálogo).
    item_response = client.post(
        f"/api/v1/sales/{sale_id}/items",
        json={"product_id": product_id, "quantity": 2},
    )
    assert item_response.status_code == 201
    item = item_response.json()["data"]
    assert item["unit_price"] == "490.00"
    assert item["total"] == "980.00"

    get_response = client.get(f"/api/v1/sales/{sale_id}")
    assert get_response.status_code == 200
    sale_detail = get_response.json()["data"]
    assert len(sale_detail["items"]) == 1
    assert sale_detail["total"] == "980.00"

    # Aplica desconto — o total é recalculado.
    update_response = client.patch(
        f"/api/v1/sales/{sale_id}", json={"discount": "80.00"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["total"] == "900.00"

    # Conclui a venda — consome o estoque do item automaticamente.
    complete_response = client.post(f"/api/v1/sales/{sale_id}/complete")
    assert complete_response.status_code == 200
    completed_sale = complete_response.json()["data"]
    assert completed_sale["status"] == "paid"

    product_after_complete = client.get(f"/api/v1/products/{product_id}")
    assert product_after_complete.json()["data"]["stock"] == 8

    stock_history = client.get(f"/api/v1/products/{product_id}/stock-movements")
    assert stock_history.json()["meta"]["total"] == 1
    assert sale_id in stock_history.json()["data"][0]["reason"]

    # Não é possível adicionar/remover item nem atualizar uma venda paga.
    add_after_paid = client.post(
        f"/api/v1/sales/{sale_id}/items", json={"product_id": product_id, "quantity": 1}
    )
    assert add_after_paid.status_code == 422

    remove_after_paid = client.delete(f"/api/v1/sales/{sale_id}/items/{item['id']}")
    assert remove_after_paid.status_code == 422

    update_after_paid = client.patch(f"/api/v1/sales/{sale_id}", json={"discount": "0.00"})
    assert update_after_paid.status_code == 422

    # Segunda venda: cancelamento.
    second_sale_response = client.post("/api/v1/sales", json={"customer_id": customer_id})
    second_sale_id = second_sale_response.json()["data"]["id"]
    cancel_response = client.post(f"/api/v1/sales/{second_sale_id}/cancel")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["data"]["status"] == "cancelled"


def test_complete_sale_rejects_insufficient_stock(auth_environment: AuthFixtureData) -> None:
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
            "sku": "SSD-VND-002",
            "name": "SSD com Pouco Estoque",
            "cost_price": "100.00",
            "sale_price": "150.00",
            "stock": 1,
        },
    )
    product_id = product_response.json()["data"]["id"]

    sale_response = client.post("/api/v1/sales", json={"customer_id": customer_id})
    sale_id = sale_response.json()["data"]["id"]

    client.post(
        f"/api/v1/sales/{sale_id}/items", json={"product_id": product_id, "quantity": 5}
    )

    complete_response = client.post(f"/api/v1/sales/{sale_id}/complete")
    assert complete_response.status_code == 409

    product_after_failed_complete = client.get(f"/api/v1/products/{product_id}")
    assert product_after_failed_complete.json()["data"]["stock"] == 1


async def test_sale_lifecycle_is_audited(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    customer_response = client.post(
        "/api/v1/customers",
        json={"type": "PF", "name": "Cliente Auditado", "document": "12345678909"},
    )
    customer_id = customer_response.json()["data"]["id"]

    sale_response = client.post("/api/v1/sales", json={"customer_id": customer_id})
    sale_id = sale_response.json()["data"]["id"]
    client.post(f"/api/v1/sales/{sale_id}/cancel")

    settings = get_settings()
    tenant_engine = create_async_engine(
        settings.tenant_database_url(auth_environment.database_name)
    )
    try:
        async with tenant_engine.connect() as connection:
            async with AsyncSession(bind=connection) as session:
                result = await session.execute(
                    select(TenantAuditLog.action).where(TenantAuditLog.resource == "sales")
                )
                actions = [row[0] for row in result.all()]
    finally:
        await tenant_engine.dispose()

    assert "SALE_CREATED" in actions
    assert "SALE_CANCELLED" in actions
