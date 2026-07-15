"""Exceções de aplicação e handlers padronizados, conforme 22-API-STANDARDS.md e
16-BACKEND-ARCHITECTURE.md ("Nunca retornar Traceback para o usuário")."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from veloai_shared.logging import get_logger
from veloai_shared.responses import ErrorResponse

logger = get_logger(__name__)


class AppException(Exception):
    """Exceção base de todo o VeloAI. Nunca deve ser levantada diretamente — sempre uma
    subclasse com `code` e `status_code` explícitos."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = "APP_ERROR"

    def __init__(
        self,
        message: str,
        *,
        errors: list[dict[str, Any]] | None = None,
        code: str | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.errors = errors or []
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code


class NotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "NOT_FOUND"


class ValidationError(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "VALIDATION_ERROR"


class ConflictError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "CONFLICT"


class PermissionDeniedError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    code = "PERMISSION_DENIED"


class AuthenticationError(AppException):
    """Credenciais ausentes, inválidas ou token expirado/malformado — usuário ainda não
    autenticado (diferente de `PermissionDeniedError`, que é para usuários autenticados
    sem permissão suficiente)."""

    status_code = status.HTTP_401_UNAUTHORIZED
    code = "AUTHENTICATION_ERROR"


class RateLimitedError(AppException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    code = "RATE_LIMITED"


def _error_body(message: str, code: str, errors: list[dict[str, Any]]) -> dict[str, Any]:
    return ErrorResponse(
        message=message,
        code=code,
        errors=errors,
        trace_id=str(uuid.uuid4()),
    ).model_dump()


def install_exception_handlers(app: FastAPI) -> None:
    """Registra os handlers de exceção padrão. Deve ser chamado por todo serviço FastAPI
    do VeloAI logo após a criação da instância `FastAPI()`."""

    @app.exception_handler(AppException)
    async def _handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        body = _error_body(exc.message, exc.code, exc.errors)
        logger.warning(
            "app_exception",
            path=request.url.path,
            method=request.method,
            code=exc.code,
            status_code=exc.status_code,
            trace_id=body["trace_id"],
        )
        return JSONResponse(status_code=exc.status_code, content=body)

    @app.exception_handler(RequestValidationError)
    async def _handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = [
            {"field": ".".join(str(part) for part in error["loc"]), "message": error["msg"]}
            for error in exc.errors()
        ]
        body = _error_body("Erro de validação nos dados enviados.", "VALIDATION_ERROR", errors)
        logger.warning(
            "validation_exception",
            path=request.url.path,
            method=request.method,
            trace_id=body["trace_id"],
        )
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=body)

    @app.exception_handler(Exception)
    async def _handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
        body = _error_body("Erro interno do servidor.", "INTERNAL_ERROR", [])
        logger.error(
            "unhandled_exception",
            path=request.url.path,
            method=request.method,
            trace_id=body["trace_id"],
            exc_info=exc,
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=body)
