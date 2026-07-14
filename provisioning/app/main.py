"""Ponto de entrada do Provisioning Service."""

from __future__ import annotations

from fastapi import FastAPI
from sqlalchemy import text
from veloai_shared import install_exception_handlers
from veloai_shared.health import build_health_router

from app.api.router import router as tenants_router
from app.core.config import get_settings
from app.core.database import dispose_engines, get_master_engine
from app.core.logging import configure_logging, get_logger

settings = get_settings()
configure_logging(service_name="provisioning", log_level=settings.log_level)
logger = get_logger(__name__)


async def _check_master_database() -> bool:
    try:
        engine = get_master_engine()
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True
    except Exception:  # noqa: BLE001 - readiness apenas reporta indisponibilidade
        return False


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Provisioning Service — único serviço com privilégios administrativos de banco.",
)

install_exception_handlers(app)
app.include_router(
    build_health_router(
        service_name="provisioning",
        readiness_checks={"master_database": _check_master_database},
    )
)
app.include_router(tenants_router)


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("provisioning_started", app_env=settings.app_env)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await dispose_engines()
