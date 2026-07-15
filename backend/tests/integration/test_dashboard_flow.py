"""Teste de ponta a ponta do módulo Dashboard (Fase 11 — núcleo operacional): login →
snapshot inicial de `/dashboard/summary` → cria cliente/fornecedor/produto com estoque
crítico → cria e conclui uma Venda (gera receita do mês) → cria e recebe uma Conta a
Receber vencida → cria e paga uma Conta a Pagar → confere que o resumo refletiu as
mudanças (deltas, não valores absolutos — o tenant é compartilhado com outros arquivos
de teste de integração) → `/dashboard/revenue-timeseries` inclui o mês corrente →
`/dashboard/top-products` inclui o produto vendido.

Reaproveita o mesmo tenant/usuário semeado por `auth_environment`
(`tests/integration/conftest.py`), que já recebe a permissão `dashboard.view` (mesmo
catálogo usado pelo seed real do Provisioning)."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from fakeredis import aioredis as fakeredis_aioredis
from fastapi.testclient import TestClient

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


def test_full_dashboard_flow(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    initial_summary = client.get("/api/v1/dashboard/summary")
    assert initial_summary.status_code == 200
    before = initial_summary.json()["data"]

    customer_response = client.post(
        "/api/v1/customers",
        json={"type": "PF", "name": "Cliente Dashboard", "document": "111.444.777-35"},
    )
    customer_id = customer_response.json()["data"]["id"]

    supplier_response = client.post(
        "/api/v1/suppliers",
        json={"type": "PJ", "name": "Fornecedor Dashboard LTDA", "document": "12345678000199"},
    )
    supplier_id = supplier_response.json()["data"]["id"]

    product_response = client.post(
        "/api/v1/products",
        json={
            "sku": "SSD-DASH-001",
            "name": "SSD para Dashboard",
            "cost_price": "320.00",
            "sale_price": "490.00",
            "stock": 1,
            "minimum_stock": 5,
        },
    )
    assert product_response.status_code == 201
    product_id = product_response.json()["data"]["id"]

    # Venda concluída no mês corrente — gera receita.
    sale_response = client.post("/api/v1/sales", json={"customer_id": customer_id})
    sale_id = sale_response.json()["data"]["id"]
    client.post(
        f"/api/v1/sales/{sale_id}/items", json={"product_id": product_id, "quantity": 1}
    )
    complete_response = client.post(f"/api/v1/sales/{sale_id}/complete")
    assert complete_response.status_code == 200
    sale_total = Decimal(complete_response.json()["data"]["total"])

    # Conta a Receber vencida, depois recebida.
    past_due_date = (date.today() - timedelta(days=3)).isoformat()
    receivable_response = client.post(
        "/api/v1/accounts-receivable",
        json={"customer_id": customer_id, "due_date": past_due_date, "amount": "150.00"},
    )
    receivable_id = receivable_response.json()["data"]["id"]
    receive_response = client.post(f"/api/v1/accounts-receivable/{receivable_id}/receive")
    assert receive_response.status_code == 200

    # Conta a Pagar paga.
    due_date = (date.today() + timedelta(days=15)).isoformat()
    payable_response = client.post(
        "/api/v1/accounts-payable",
        json={"supplier_id": supplier_id, "due_date": due_date, "amount": "80.00"},
    )
    payable_id = payable_response.json()["data"]["id"]
    pay_response = client.post(f"/api/v1/accounts-payable/{payable_id}/pay")
    assert pay_response.status_code == 200

    after_summary = client.get("/api/v1/dashboard/summary")
    assert after_summary.status_code == 200
    after = after_summary.json()["data"]

    assert after["total_customers"] == before["total_customers"] + 1
    assert after["total_products"] == before["total_products"] + 1
    assert after["critical_stock_count"] >= before["critical_stock_count"] + 1
    assert Decimal(after["revenue_this_month"]) >= Decimal(before["revenue_this_month"]) + sale_total
    # A conta a receber foi recebida (não fica pendente) — o saldo de caixa sobe com o
    # recebimento (+150.00) e desce com o pagamento (-80.00), líquido +70.00.
    assert Decimal(after["cash_balance"]) == Decimal(before["cash_balance"]) + Decimal("70.00")
    assert after["accounts_payable_pending_total"] == before["accounts_payable_pending_total"]

    timeseries_response = client.get("/api/v1/dashboard/revenue-timeseries")
    assert timeseries_response.status_code == 200
    timeseries = timeseries_response.json()["data"]
    assert len(timeseries) == 6
    current_period = date.today().strftime("%Y-%m")
    assert timeseries[-1]["period"] == current_period

    top_products_response = client.get("/api/v1/dashboard/top-products?limit=5")
    assert top_products_response.status_code == 200
    top_products = top_products_response.json()["data"]
    assert any(item["product_id"] == product_id for item in top_products)
