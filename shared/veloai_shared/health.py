"""Router de Health Check reutilizável, conforme 16-BACKEND-ARCHITECTURE.md e
26-OBSERVABILITY.md (`/health`, `/ready`, `/live`)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from veloai_shared.responses import SuccessResponse

ReadinessCheck = Callable[[], Awaitable[bool]]


class HealthStatus(BaseModel):
    """Payload retornado pelos endpoints de saúde."""

    status: str
    service: str
    checks: dict[str, bool] = {}


def build_health_router(
    *,
    service_name: str,
    readiness_checks: dict[str, ReadinessCheck] | None = None,
) -> APIRouter:
    """Cria um APIRouter com `/health`, `/ready` e `/live`.

    `readiness_checks` é um dicionário nome -> corrotina que retorna `True` quando a
    dependência (banco, cache, etc.) está disponível. Usado apenas por `/ready`.
    """

    router = APIRouter(tags=["system"])
    checks = readiness_checks or {}

    @router.get("/health")
    async def health() -> SuccessResponse[HealthStatus]:
        payload = HealthStatus(status="ok", service=service_name)
        return SuccessResponse(message="Serviço saudável.", data=payload)

    @router.get("/live")
    async def live() -> SuccessResponse[HealthStatus]:
        payload = HealthStatus(status="ok", service=service_name)
        return SuccessResponse(message="Processo em execução.", data=payload)

    @router.get("/ready")
    async def ready() -> Any:
        results: dict[str, bool] = {}
        for name, check in checks.items():
            try:
                results[name] = await check()
            except Exception:  # noqa: BLE001 - readiness nunca pode derrubar o serviço
                results[name] = False

        all_ok = all(results.values()) if results else True
        payload = HealthStatus(
            status="ok" if all_ok else "degraded",
            service=service_name,
            checks=results,
        )
        response = SuccessResponse(
            message="Pronto." if all_ok else "Dependências indisponíveis.",
            data=payload,
        )
        if all_ok:
            return response
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=response.model_dump(),
        )

    return router
