"""Teste de ponta a ponta do módulo de Autenticação: login com senha temporária →
troca de senha obrigatória → login com a senha nova → `/me` → refresh (rotação) →
logout (revogação) — usando um tenant e usuário reais, criados por `auth_environment`
(ver `conftest.py`).

O rate limiter usa um Redis falso (`fakeredis`) apenas para isolar este teste de
qualquer estado residual de execuções anteriores — a lógica de rate limit em si já é
coberta por `tests/unit/auth/test_rate_limit.py`."""

from __future__ import annotations

from fakeredis import aioredis as fakeredis_aioredis
from fastapi.testclient import TestClient

from app.core.rate_limit import LoginRateLimiter, get_login_rate_limiter
from app.main import app

from .conftest import AuthFixtureData

app.dependency_overrides[get_login_rate_limiter] = lambda: LoginRateLimiter(
    fakeredis_aioredis.FakeRedis(decode_responses=True)
)


def test_full_authentication_flow(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)

    # 1. Login com a senha temporária semeada pelo Provisioning.
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": auth_environment.user_email,
            "password": auth_environment.temporary_password,
        },
    )
    assert login_response.status_code == 200
    login_body = login_response.json()
    assert login_body["success"] is True
    assert login_body["data"]["must_change_password"] is True
    assert login_body["data"]["role"] == "Administrador"
    assert "system.admin" in login_body["data"]["permissions"]
    assert "access_token" in client.cookies
    assert "refresh_token" in client.cookies

    # 2. `/me` reflete o mesmo usuário, usando apenas o cookie.
    me_response = client.get("/api/v1/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["data"]["email"] == auth_environment.user_email
    assert me_response.json()["data"]["must_change_password"] is True

    # 3. Senha errada nunca revela se o e-mail existe.
    wrong_password_response = client.post(
        "/api/v1/auth/login",
        json={"email": auth_environment.user_email, "password": "senha-errada"},
    )
    assert wrong_password_response.status_code == 401
    assert wrong_password_response.json()["code"] == "INVALID_CREDENTIALS"

    # 4. Troca de senha obrigatória.
    change_password_response = client.patch(
        "/api/v1/auth/password",
        json={
            "current_password": auth_environment.temporary_password,
            "new_password": "NovaSenhaForte123!",
        },
    )
    assert change_password_response.status_code == 200

    # 5. `must_change_password` volta a `False`.
    me_after_change = client.get("/api/v1/auth/me")
    assert me_after_change.json()["data"]["must_change_password"] is False

    # 6. A senha temporária antiga não funciona mais.
    old_password_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": auth_environment.user_email,
            "password": auth_environment.temporary_password,
        },
    )
    assert old_password_login.status_code == 401

    # 7. A nova senha funciona e emite um novo par de cookies.
    new_password_login = client.post(
        "/api/v1/auth/login",
        json={"email": auth_environment.user_email, "password": "NovaSenhaForte123!"},
    )
    assert new_password_login.status_code == 200
    old_refresh_cookie = client.cookies.get("refresh_token")

    # 8. Refresh rotaciona o refresh token (o valor muda a cada renovação).
    refresh_response = client.post("/api/v1/auth/refresh")
    assert refresh_response.status_code == 200
    new_refresh_cookie = client.cookies.get("refresh_token")
    assert new_refresh_cookie != old_refresh_cookie

    # 9. Logout revoga o refresh token corrente e limpa os cookies.
    logout_response = client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 200

    # 10. Após o logout, o access token foi limpo — `/me` exige novo login.
    me_after_logout = client.get("/api/v1/auth/me")
    assert me_after_logout.status_code == 401


def test_login_with_unknown_email_returns_generic_invalid_credentials(
    auth_environment: AuthFixtureData,
) -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nao-existe@empresa.test", "password": "qualquer-coisa"},
    )

    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_CREDENTIALS"


def test_me_without_cookie_requires_authentication(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["code"] == "NOT_AUTHENTICATED"


def test_refresh_without_cookie_requires_authentication(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)

    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 401


def test_expired_or_reused_refresh_token_is_rejected(auth_environment: AuthFixtureData) -> None:
    # Depende de `test_full_authentication_flow` já ter trocado a senha temporária
    # (pytest executa os testes de um módulo na ordem em que estão definidos aqui).
    client = TestClient(app)
    client.post(
        "/api/v1/auth/login",
        json={
            "email": auth_environment.user_email,
            "password": "NovaSenhaForte123!",
        },
    )

    # Usa o refresh token uma vez (rotaciona) e tenta reutilizar o valor antigo.
    old_refresh_cookie = client.cookies.get("refresh_token")
    client.post("/api/v1/auth/refresh")

    client.cookies.set("refresh_token", old_refresh_cookie)
    reused_response = client.post("/api/v1/auth/refresh")

    assert reused_response.status_code == 401
