"""Configuração central de logs estruturados (Structlog), conforme 16-BACKEND-ARCHITECTURE.md
e 26-OBSERVABILITY.md. Nunca utilizar print()/console.log() — sempre este logger."""

from __future__ import annotations

import logging
import sys

import structlog


def configure_logging(*, service_name: str, log_level: str = "INFO") -> None:
    """Configura o Structlog para emitir logs em JSON com os campos obrigatórios de
    correlação (service, level, timestamp). Deve ser chamado uma única vez, na
    inicialização de cada serviço."""

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    structlog.contextvars.bind_contextvars(service=service_name)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Retorna um logger estruturado. Nunca registrar senhas, tokens ou dados sensíveis."""

    return structlog.get_logger(name)
