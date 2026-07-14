from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["service"] == "backend"


def test_ready_endpoint_ok_without_dependencies() -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ok"


def test_live_endpoint() -> None:
    response = client.get("/live")

    assert response.status_code == 200


def test_openapi_schema_has_correct_title_and_version() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "VeloAI Backend"
    assert schema["info"]["version"] == "0.1.0"


def test_unknown_route_returns_standard_404_envelope() -> None:
    response = client.get("/nao-existe")

    assert response.status_code == 404
