from fastapi import FastAPI
from fastapi.testclient import TestClient

from veloai_shared.health import build_health_router


def test_health_and_live_always_ok() -> None:
    app = FastAPI()
    app.include_router(build_health_router(service_name="backend"))
    client = TestClient(app)

    for path in ("/health", "/live"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "ok"


def test_ready_returns_200_when_all_checks_pass() -> None:
    async def _ok() -> bool:
        return True

    app = FastAPI()
    app.include_router(
        build_health_router(service_name="provisioning", readiness_checks={"database": _ok})
    )
    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["data"]["checks"] == {"database": True}


def test_ready_returns_503_when_a_check_fails() -> None:
    async def _fail() -> bool:
        return False

    app = FastAPI()
    app.include_router(
        build_health_router(service_name="provisioning", readiness_checks={"database": _fail})
    )
    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["data"]["status"] == "degraded"


def test_ready_handles_check_that_raises() -> None:
    async def _raises() -> bool:
        raise ConnectionError("db down")

    app = FastAPI()
    app.include_router(
        build_health_router(service_name="provisioning", readiness_checks={"database": _raises})
    )
    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["data"]["checks"]["database"] is False
