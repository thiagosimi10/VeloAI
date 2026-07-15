import httpx
import respx
from fakeredis import aioredis as fakeredis_aioredis
from fastapi.testclient import TestClient

import app.api.router as router_module
from app.core.config import get_settings
from app.main import app

client = TestClient(app)


def _use_fake_redis(monkeypatch):
    """Evita que os testes de `/generate` dependam de um Redis real acessível pelo
    hostname `redis` (só existe dentro do docker-compose) — mesmo padrão de
    `fakeredis` já usado nos testes de rate limit do Backend. Retorna a mesma instância
    a cada chamada, para que requisições sucessivas no teste compartilhem o cache."""

    fake_redis = fakeredis_aioredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(router_module, "get_redis_client", lambda: fake_redis)
    return fake_redis


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["data"]["service"] == "ai-gateway"


def test_ready_is_degraded_without_api_key(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("GEMINI_API_KEY", "")

    response = client.get("/ready")

    assert response.status_code == 503
    get_settings.cache_clear()


def test_ready_is_ok_with_api_key(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

    response = client.get("/ready")

    assert response.status_code == 200
    get_settings.cache_clear()


def test_models_endpoint_lists_configured_model(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

    response = client.get("/models")

    assert response.status_code == 200
    assert response.json()["data"] == ["gemini-3.1-flash-lite"]
    get_settings.cache_clear()


def test_generate_endpoint_returns_standard_envelope(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    _use_fake_redis(monkeypatch)

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-3.1-flash-lite:generateContent"
    )
    with respx.mock:
        respx.post(url).mock(
            return_value=httpx.Response(
                200,
                json={"candidates": [{"content": {"parts": [{"text": "resposta"}]}}]},
            )
        )
        response = client.post("/generate", json={"prompt": "Olá"})

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["text"] == "resposta"
    assert body["data"]["cached"] is False
    assert float(body["data"]["estimated_cost"]) >= 0
    get_settings.cache_clear()


def test_generate_endpoint_second_identical_call_is_served_from_cache(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    _use_fake_redis(monkeypatch)

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-3.1-flash-lite:generateContent"
    )
    with respx.mock:
        route = respx.post(url).mock(
            return_value=httpx.Response(
                200,
                json={"candidates": [{"content": {"parts": [{"text": "resposta"}]}}]},
            )
        )
        first_response = client.post("/generate", json={"prompt": "Qual o resumo de hoje?"})
        second_response = client.post("/generate", json={"prompt": "Qual o resumo de hoje?"})

        assert route.call_count == 1

    assert first_response.json()["data"]["cached"] is False
    assert second_response.json()["data"]["cached"] is True
    assert second_response.json()["data"]["text"] == "resposta"
    get_settings.cache_clear()


def test_generate_endpoint_rejects_empty_prompt() -> None:
    response = client.post("/generate", json={"prompt": ""})

    assert response.status_code == 422
