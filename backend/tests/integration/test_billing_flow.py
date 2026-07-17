"""Teste de ponta a ponta do módulo de Billing (Fase 17): login → `GET
/billing/subscription` reflete a Assinatura ACTIVE real criada pela fixture → `POST
/billing/cancel` cancela de verdade → uma rota de negócio qualquer (`GET /customers`)
passa a responder 403 `SUBSCRIPTION_INACTIVE` → `GET /billing/subscription` continua
acessível mesmo cancelada (nunca fica atrás do gate).

O tenant de teste é compartilhado por toda a suíte de integração (`auth_environment` é
`scope="session"`) — por isso o cancelamento é sempre revertido em um `finally`, para
não deixar as demais suítes vendo uma assinatura inativa."""

from __future__ import annotations

import uuid

from fakeredis import aioredis as fakeredis_aioredis
from fastapi.testclient import TestClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import create_async_engine
from veloai_shared.schema.master import Subscription, SubscriptionStatus

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


async def _set_subscription_status(tenant_id: uuid.UUID, status: SubscriptionStatus) -> None:
    engine = create_async_engine(get_settings().master_database_url)
    try:
        async with engine.begin() as connection:
            await connection.execute(
                update(Subscription)
                .where(Subscription.tenant_id == tenant_id)
                .values(status=status.value)
            )
    finally:
        await engine.dispose()


async def test_billing_subscription_flow(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    try:
        get_response = client.get("/api/v1/billing/subscription")
        assert get_response.status_code == 200, get_response.text
        data = get_response.json()["data"]
        assert data["plan_name"] == "VeloAI Professional"
        assert data["status"] == SubscriptionStatus.ACTIVE.value

        cancel_response = client.post("/api/v1/billing/cancel")
        assert cancel_response.status_code == 200, cancel_response.text
        assert cancel_response.json()["data"]["status"] == SubscriptionStatus.CANCELED.value

        blocked_response = client.get("/api/v1/customers")
        assert blocked_response.status_code == 403, blocked_response.text
        assert blocked_response.json()["code"] == "SUBSCRIPTION_INACTIVE"

        still_visible = client.get("/api/v1/billing/subscription")
        assert still_visible.status_code == 200, still_visible.text
        assert still_visible.json()["data"]["status"] == SubscriptionStatus.CANCELED.value

        already_canceled = client.post("/api/v1/billing/cancel")
        assert already_canceled.status_code == 409, already_canceled.text
    finally:
        await _set_subscription_status(auth_environment.tenant_id, SubscriptionStatus.ACTIVE)
