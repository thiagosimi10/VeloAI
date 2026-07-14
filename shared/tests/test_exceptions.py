from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from veloai_shared.exceptions import ConflictError, NotFoundError, install_exception_handlers


class _Payload(BaseModel):
    name: str


def _build_app() -> FastAPI:
    app = FastAPI()
    install_exception_handlers(app)

    @app.get("/not-found")
    async def _raise_not_found() -> None:
        raise NotFoundError("Cliente não encontrado.", code="CUSTOMER_NOT_FOUND")

    @app.get("/conflict")
    async def _raise_conflict() -> None:
        raise ConflictError("Já existe um tenant com este documento.")

    @app.get("/boom")
    async def _raise_unexpected() -> None:
        raise RuntimeError("algo quebrou internamente")

    @app.post("/validate")
    async def _validate(payload: _Payload) -> dict[str, str]:
        return {"name": payload.name}

    return app


def test_app_exception_returns_standard_envelope() -> None:
    client = TestClient(_build_app(), raise_server_exceptions=False)

    response = client.get("/not-found")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["code"] == "CUSTOMER_NOT_FOUND"
    assert body["message"] == "Cliente não encontrado."
    assert "trace_id" in body


def test_conflict_error_returns_409() -> None:
    client = TestClient(_build_app(), raise_server_exceptions=False)

    response = client.get("/conflict")

    assert response.status_code == 409
    assert response.json()["code"] == "CONFLICT"


def test_unexpected_exception_never_leaks_traceback() -> None:
    client = TestClient(_build_app(), raise_server_exceptions=False)

    response = client.get("/boom")

    assert response.status_code == 500
    body = response.json()
    assert body["code"] == "INTERNAL_ERROR"
    assert "RuntimeError" not in body["message"]
    assert "Traceback" not in str(body)


def test_validation_error_returns_422_with_field_errors() -> None:
    client = TestClient(_build_app(), raise_server_exceptions=False)

    response = client.post("/validate", json={})

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert body["errors"][0]["field"] == "name"
