"""Teste de ponta a ponta do módulo de IA (Fase 13): login → `POST /ai/ask` → grava uma
linha em `ai_conversations` (tokens/modelo/tempo de execução) e em `TenantAuditLog` →
`GET /ai/conversations` reflete o histórico.

O AI Gateway real (que chamaria o Gemini de verdade) é substituído por um dependency
override com uma resposta fixa — mesmo critério já usado para `get_login_rate_limiter`
em `test_attachments_flow.py`: chamar um provedor de LLM de verdade em CI não é
desejável nem determinístico."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient
from fakeredis import aioredis as fakeredis_aioredis

from app.core.ai_gateway_client import AIGatewayResult, get_ai_gateway_client
from app.core.rate_limit import LoginRateLimiter, get_login_rate_limiter
from app.main import app

from .conftest import AuthFixtureData

app.dependency_overrides[get_login_rate_limiter] = lambda: LoginRateLimiter(
    fakeredis_aioredis.FakeRedis(decode_responses=True)
)

_FAKE_RESULT = AIGatewayResult(
    text="Você vendeu R$ 12.340,00 em maio.",
    model="gemini-3.1-flash-lite",
    input_tokens=40,
    output_tokens=20,
    cached=False,
    estimated_cost=Decimal("0.0000120"),
)


def _fake_ai_gateway_client() -> MagicMock:
    client = MagicMock()
    client.generate = AsyncMock(return_value=_FAKE_RESULT)
    return client


def _login(client: TestClient, fixture: AuthFixtureData, password: str) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": fixture.user_email, "password": password},
    )
    assert response.status_code == 200


def test_ask_ai_persists_conversation_and_is_listed(auth_environment: AuthFixtureData) -> None:
    fake_client = _fake_ai_gateway_client()
    app.dependency_overrides[get_ai_gateway_client] = lambda: fake_client
    try:
        client = TestClient(app)
        _login(client, auth_environment, auth_environment.temporary_password)

        ask_response = client.post("/api/v1/ai/ask", json={"prompt": "Quanto vendi em maio?"})

        assert ask_response.status_code == 200, ask_response.text
        data = ask_response.json()["data"]
        assert data["response"] == "Você vendeu R$ 12.340,00 em maio."
        assert data["model"] == "gemini-3.1-flash-lite"
        assert data["tokens"] == 60
        assert data["cached"] is False
        assert Decimal(str(data["estimated_cost"])) == Decimal("0.0000120")

        fake_client.generate.assert_awaited_once()
        system_prompt = fake_client.generate.call_args.kwargs["system_prompt"]
        assert "Assistência Técnica Silva" in system_prompt
        assert "Maria Souza" in system_prompt

        list_response = client.get("/api/v1/ai/conversations")
        assert list_response.status_code == 200
        items = list_response.json()["data"]
        assert len(items) == 1
        assert items[0]["prompt"] == "Quanto vendi em maio?"
        assert items[0]["response"] == "Você vendeu R$ 12.340,00 em maio."
        assert items[0]["tokens"] == 60
    finally:
        del app.dependency_overrides[get_ai_gateway_client]


def test_ask_ai_requires_authentication() -> None:
    client = TestClient(app)

    response = client.post("/api/v1/ai/ask", json={"prompt": "Quanto vendi em maio?"})

    assert response.status_code == 401
