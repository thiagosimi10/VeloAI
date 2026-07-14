"""Ponto de entrada do Backend (API principal do VeloAI).

Nesta fase de fundação este serviço não possui conexão a banco de dados nem módulos de
negócio: a resolução de Tenant depende da Autenticação (Fase 3 do Master Plan), ainda não
implementada. Ver decisão registrada no plano de fundação."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from veloai_shared import install_exception_handlers
from veloai_shared.health import build_health_router

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger

settings = get_settings()
configure_logging(service_name="backend", log_level=settings.log_level)
logger = get_logger(__name__)

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

install_exception_handlers(app)
app.include_router(build_health_router(service_name="backend"))
app.include_router(api_v1_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("backend_started", app_env=settings.app_env)
