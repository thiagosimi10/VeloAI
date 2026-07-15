"""Teste de ponta a ponta do módulo Financeiro (Fase 10 — núcleo operacional): login →
criar cliente/fornecedor → criar conta a receber → `receive` → confere lançamento
automático em `cash_flow` (`type="in"`) → criar conta a pagar → `pay` → confere
lançamento automático (`type="out"`) → lançamento avulso manual → cancelar uma conta
pendente → update bloqueado após `received`/`paid`/`cancelled` → auditoria gravada.

Reaproveita o mesmo tenant/usuário semeado por `auth_environment`
(`tests/integration/conftest.py`), que já recebe as permissões `finance.*` (mesmo
catálogo usado pelo seed real do Provisioning)."""

from __future__ import annotations

from datetime import date, timedelta

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


def test_full_finance_flow(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    customer_response = client.post(
        "/api/v1/customers",
        json={"type": "PF", "name": "Cliente Financeiro", "document": "111.444.777-35"},
    )
    assert customer_response.status_code == 201
    customer_id = customer_response.json()["data"]["id"]

    supplier_response = client.post(
        "/api/v1/suppliers",
        json={"type": "PJ", "name": "Fornecedor Financeiro LTDA", "document": "12345678000199"},
    )
    assert supplier_response.status_code == 201
    supplier_id = supplier_response.json()["data"]["id"]

    due_date = (date.today() + timedelta(days=15)).isoformat()

    # Conta a Receber: criar → receber → confere lançamento automático no fluxo.
    receivable_response = client.post(
        "/api/v1/accounts-receivable",
        json={"customer_id": customer_id, "due_date": due_date, "amount": "980.00"},
    )
    assert receivable_response.status_code == 201
    receivable = receivable_response.json()["data"]
    assert receivable["status"] == "pending"
    assert receivable["is_overdue"] is False
    receivable_id = receivable["id"]

    receive_response = client.post(f"/api/v1/accounts-receivable/{receivable_id}/receive")
    assert receive_response.status_code == 200
    received = receive_response.json()["data"]
    assert received["status"] == "received"
    assert received["payment_date"] == date.today().isoformat()

    # Update bloqueado depois de recebida.
    update_after_received = client.patch(
        f"/api/v1/accounts-receivable/{receivable_id}", json={"amount": "500.00"}
    )
    assert update_after_received.status_code == 422

    cash_flow_after_receive = client.get("/api/v1/cash-flow?type=in")
    assert cash_flow_after_receive.status_code == 200
    in_entries = cash_flow_after_receive.json()["data"]
    assert any(
        entry["category"] == "Recebimento" and entry["amount"] == "980.00"
        for entry in in_entries
    )

    # Conta a Pagar: criar → pagar → confere lançamento automático no fluxo.
    payable_response = client.post(
        "/api/v1/accounts-payable",
        json={"supplier_id": supplier_id, "due_date": due_date, "amount": "320.00"},
    )
    assert payable_response.status_code == 201
    payable_id = payable_response.json()["data"]["id"]

    pay_response = client.post(f"/api/v1/accounts-payable/{payable_id}/pay")
    assert pay_response.status_code == 200
    paid = pay_response.json()["data"]
    assert paid["status"] == "paid"
    assert paid["payment_date"] == date.today().isoformat()

    cash_flow_after_pay = client.get("/api/v1/cash-flow?type=out")
    assert cash_flow_after_pay.status_code == 200
    out_entries = cash_flow_after_pay.json()["data"]
    assert any(
        entry["category"] == "Pagamento" and entry["amount"] == "320.00" for entry in out_entries
    )

    # Lançamento avulso manual.
    manual_entry_response = client.post(
        "/api/v1/cash-flow",
        json={
            "type": "out",
            "category": "Despesas Administrativas",
            "description": "Aluguel",
            "amount": "1500.00",
        },
    )
    assert manual_entry_response.status_code == 201
    assert manual_entry_response.json()["data"]["category"] == "Despesas Administrativas"

    # Segunda Conta a Receber: cancelamento (nenhum lançamento gerado).
    second_receivable_response = client.post(
        "/api/v1/accounts-receivable",
        json={"customer_id": customer_id, "due_date": due_date, "amount": "200.00"},
    )
    second_receivable_id = second_receivable_response.json()["data"]["id"]
    cancel_response = client.post(
        f"/api/v1/accounts-receivable/{second_receivable_id}/cancel"
    )
    assert cancel_response.status_code == 200
    assert cancel_response.json()["data"]["status"] == "cancelled"

    # Update bloqueado depois de cancelada.
    update_after_cancelled = client.patch(
        f"/api/v1/accounts-receivable/{second_receivable_id}", json={"amount": "999.00"}
    )
    assert update_after_cancelled.status_code == 422


def test_account_receivable_is_overdue_when_due_date_has_passed(
    auth_environment: AuthFixtureData,
) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    customer_response = client.post(
        "/api/v1/customers",
        json={"type": "PF", "name": "Cliente Vencido", "document": "98765432100"},
    )
    customer_id = customer_response.json()["data"]["id"]

    past_due_date = (date.today() - timedelta(days=5)).isoformat()
    receivable_response = client.post(
        "/api/v1/accounts-receivable",
        json={"customer_id": customer_id, "due_date": past_due_date, "amount": "150.00"},
    )
    assert receivable_response.status_code == 201
    assert receivable_response.json()["data"]["is_overdue"] is True


async def test_finance_lifecycle_is_audited(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    customer_response = client.post(
        "/api/v1/customers",
        json={"type": "PF", "name": "Cliente Auditado Financeiro", "document": "12345678909"},
    )
    customer_id = customer_response.json()["data"]["id"]

    due_date = (date.today() + timedelta(days=10)).isoformat()
    receivable_response = client.post(
        "/api/v1/accounts-receivable",
        json={"customer_id": customer_id, "due_date": due_date, "amount": "300.00"},
    )
    receivable_id = receivable_response.json()["data"]["id"]
    client.post(f"/api/v1/accounts-receivable/{receivable_id}/receive")

    settings = get_settings()
    tenant_engine = create_async_engine(
        settings.tenant_database_url(auth_environment.database_name)
    )
    try:
        async with tenant_engine.connect() as connection:
            async with AsyncSession(bind=connection) as session:
                result = await session.execute(
                    select(TenantAuditLog.action).where(TenantAuditLog.resource == "finance")
                )
                actions = [row[0] for row in result.all()]
    finally:
        await tenant_engine.dispose()

    assert "ACCOUNT_RECEIVABLE_CREATED" in actions
    assert "ACCOUNT_RECEIVABLE_RECEIVED" in actions
