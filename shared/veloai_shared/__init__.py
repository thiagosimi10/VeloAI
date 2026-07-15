"""Utilitários compartilhados entre os serviços Python do VeloAI."""

from veloai_shared.exceptions import (
    AppException,
    AuthenticationError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitedError,
    ValidationError,
    install_exception_handlers,
)
from veloai_shared.health import HealthStatus, build_health_router
from veloai_shared.logging import configure_logging, get_logger
from veloai_shared.responses import ErrorResponse, PaginationMeta, SuccessResponse
from veloai_shared.validators import normalize_document

__all__ = [
    "AppException",
    "AuthenticationError",
    "ConflictError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitedError",
    "ValidationError",
    "install_exception_handlers",
    "HealthStatus",
    "build_health_router",
    "configure_logging",
    "get_logger",
    "ErrorResponse",
    "PaginationMeta",
    "SuccessResponse",
    "normalize_document",
]
