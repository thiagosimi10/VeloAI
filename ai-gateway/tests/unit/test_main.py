import httpx
import respx
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app

client = TestClient(app)


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
    get_settings.cache_clear()


def test_generate_endpoint_rejects_empty_prompt() -> None:
    response = client.post("/generate", json={"prompt": ""})

    assert response.status_code == 422
