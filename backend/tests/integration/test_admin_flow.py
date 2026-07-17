"""Teste de ponta a ponta do Painel Administrativo (Fase 18): login de Platform Admin
(sessão totalmente separada da de tenant) → `GET /admin/tenants` reflete o tenant real
criado por `auth_environment` (com plano/assinatura da Fase 17) → `GET /admin/summary`
com contagens reais → `GET /admin/tenants/{id}/audit-log` → logout. Também confirma que
um cookie de tenant nunca autentica uma rota de admin e vice-versa."""

from __future__ import annotations

from fakeredis import aioredis as fakeredis_aioredis
from fastapi.testclient import TestClient

from app.core.rate_limit import LoginRateLimiter, get_login_rate_limiter
from app.main import app

from .conftest import AuthFixtureData

app.dependency_overrides[get_login_rate_limiter] = lambda: LoginRateLimiter(
    fakeredis_aioredis.FakeRedis(decode_responses=True)
)


def _admin_login(client: TestClient, fixture: AuthFixtureData) -> None:
    response = client.post(
        "/api/v1/admin/auth/login",
        json={
            "email": fixture.platform_admin_email,
            "password": fixture.platform_admin_password,
        },
    )
    assert response.status_code == 200, response.text


def test_admin_can_login_and_list_tenants(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _admin_login(client, auth_environment)

    me_response = client.get("/api/v1/admin/auth/me")
    assert me_response.status_code == 200, me_response.text
    assert me_response.json()["data"]["email"] == auth_environment.platform_admin_email

    tenants_response = client.get("/api/v1/admin/tenants")
    assert tenants_response.status_code == 200, tenants_response.text
    tenants = tenants_response.json()["data"]
    matching = [item for item in tenants if item["tenant_id"] == str(auth_environment.tenant_id)]
    assert len(matching) == 1
    assert matching[0]["plan_name"] == "VeloAI Professional"
    assert matching[0]["subscription_status"] == "ACTIVE"

    summary_response = client.get("/api/v1/admin/summary")
    assert summary_response.status_code == 200, summary_response.text
    summary = summary_response.json()["data"]
    assert summary["total_tenants"] >= 1
    assert summary["active_count"] >= 1

    audit_log_response = client.get(
        f"/api/v1/admin/tenants/{auth_environment.tenant_id}/audit-log"
    )
    assert audit_log_response.status_code == 200, audit_log_response.text

    logout_response = client.post("/api/v1/admin/auth/logout")
    assert logout_response.status_code == 200, logout_response.text

    after_logout_response = client.get("/api/v1/admin/tenants")
    assert after_logout_response.status_code == 401


def test_admin_login_rejects_wrong_password(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/admin/auth/login",
        json={"email": auth_environment.platform_admin_email, "password": "senha-errada"},
    )

    assert response.status_code == 401, response.text
    assert response.json()["code"] == "INVALID_CREDENTIALS"


def test_tenant_session_cookie_never_authenticates_admin_routes(
    auth_environment: AuthFixtureData,
) -> None:
    client = TestClient(app)
    tenant_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": auth_environment.user_email,
            "password": auth_environment.temporary_password,
        },
    )
    assert tenant_login.status_code == 200, tenant_login.text

    admin_response = client.get("/api/v1/admin/tenants")
    assert admin_response.status_code == 401


def test_admin_session_cookie_never_authenticates_tenant_routes(
    auth_environment: AuthFixtureData,
) -> None:
    client = TestClient(app)
    _admin_login(client, auth_environment)

    tenant_response = client.get("/api/v1/auth/me")
    assert tenant_response.status_code == 401
