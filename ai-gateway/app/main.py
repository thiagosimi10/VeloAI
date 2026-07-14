"""Ponto de entrada do AI Gateway — único serviço autorizado a se comunicar com
provedores de LLM, conforme 28-AI-GATEWAY.md ("Nenhuma LLM poderá ser chamada
diretamente [por outro serviço].")."""

from __future__ import annotations

from fastapi import FastAPI
from veloai_shared import install_exception_handlers
from veloai_shared.health import build_health_router

from app.api.router import router as ai_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.providers.factory import get_provider

settings = get_settings()
configure_logging(service_name="ai-gateway", log_level=settings.log_level)
logger = get_logger(__name__)


async def _check_provider_configured() -> bool:
    provider = get_provider(settings)
    return await provider.health_check()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI Gateway — ponto único de comunicação com provedores de LLM.",
)

install_exception_handlers(app)
app.include_router(
    build_health_router(
        service_name="ai-gateway",
        readiness_checks={"provider": _check_provider_configured},
    )
)
app.include_router(ai_router)


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("ai_gateway_started", app_env=settings.app_env, provider=settings.ai_provider)
