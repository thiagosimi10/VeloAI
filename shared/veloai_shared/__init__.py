"""Utilitários compartilhados entre os serviços Python do VeloAI."""

from veloai_shared.exceptions import (
    AppException,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
    install_exception_handlers,
)
from veloai_shared.health import HealthStatus, build_health_router
from veloai_shared.logging import configure_logging, get_logger
from veloai_shared.responses import ErrorResponse, PaginationMeta, SuccessResponse

__all__ = [
    "AppException",
    "ConflictError",
    "NotFoundError",
    "PermissionDeniedError",
    "ValidationError",
    "install_exception_handlers",
    "HealthStatus",
    "build_health_router",
    "configure_logging",
    "get_logger",
    "ErrorResponse",
    "PaginationMeta",
    "SuccessResponse",
]
