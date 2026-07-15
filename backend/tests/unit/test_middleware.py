from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_response_includes_request_id_header() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert "x-request-id" in response.headers


def test_propagates_client_supplied_request_id() -> None:
    response = client.get("/health", headers={"X-Request-ID": "custom-id-123"})

    assert response.headers["x-request-id"] == "custom-id-123"


def test_generates_a_new_request_id_when_not_supplied() -> None:
    response_one = client.get("/health")
    response_two = client.get("/health")

    assert response_one.headers["x-request-id"] != response_two.headers["x-request-id"]
