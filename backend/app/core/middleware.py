"""Middleware de log estruturado por requisição, conforme 16-BACKEND-ARCHITECTURE.md
("Registrar: Request, Response, Tempo, Usuário, Tenant, IP, Erro.") e
26-OBSERVABILITY.md ("Todo endpoint deverá gerar Trace ID.")."""

from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

REQUEST_ID_HEADER = "X-Request-ID"

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Gera/propaga um `X-Request-ID`, vincula-o ao contexto do Structlog durante toda
    a requisição e loga início/fim com método, path, status e duração."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        start_time = time.perf_counter()

        structlog.contextvars.bind_contextvars(request_id=request_id)
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
            )
            raise
        else:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            response.headers[REQUEST_ID_HEADER] = request_id
            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )
            return response
        finally:
            structlog.contextvars.unbind_contextvars("request_id")
