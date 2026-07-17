"""Ponto de entrada do Backend (API principal do VeloAI).

Autentica-se no PostgreSQL exclusivamente como a role `veloai_app` (nunca a role
administrativa do Provisioning) e resolve a conexão do tenant dinamicamente a partir do
Banco Master, conforme 04-MULTI-TENANCY.md."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from veloai_shared import install_exception_handlers
from veloai_shared.health import build_health_router

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.database import dispose_engines, get_master_engine
from app.core.logging import configure_logging, get_logger
from app.core.middleware import RequestLoggingMiddleware
from app.core.qdrant_client import get_qdrant_client
from app.core.rate_limit import get_redis_client
from app.core.storage import get_storage_client

settings = get_settings()
configure_logging(service_name="backend", log_level=settings.log_level)
logger = get_logger(__name__)


async def _check_master_database() -> bool:
    try:
        engine = get_master_engine()
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True
    except Exception:  # noqa: BLE001 - readiness apenas reporta indisponibilidade
        return False


async def _check_redis() -> bool:
    try:
        await get_redis_client().ping()
        return True
    except Exception:  # noqa: BLE001 - readiness apenas reporta indisponibilidade
        return False


async def _check_storage() -> bool:
    return await get_storage_client().is_reachable()


async def _check_qdrant() -> bool:
    return await get_qdrant_client().is_reachable()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API principal do VeloAI — AI Business OS.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

install_exception_handlers(app)
app.include_router(
    build_health_router(
        service_name="backend",
        readiness_checks={
            "master_database": _check_master_database,
            "redis": _check_redis,
            "storage": _check_storage,
            "qdrant": _check_qdrant,
        },
    )
)
app.include_router(api_v1_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
async def on_startup() -> None:
    try:
        await get_storage_client().ensure_bucket_exists()
    except Exception:  # noqa: BLE001 - MinIO indisponível não deve impedir o boot;
        # `/ready` já reporta "storage" separadamente (`_check_storage`).
        logger.warning("storage_bucket_check_failed", app_env=settings.app_env)
    logger.info("backend_started", app_env=settings.app_env)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await dispose_engines()
    await get_redis_client().aclose()
