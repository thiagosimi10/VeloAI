"""Dependências de autenticação do Painel Administrativo — deliberadamente paralelas
às de `app/core/dependencies.py` (`get_current_user`/`CurrentUser`), nunca as
reaproveitando: um Platform Admin não tem `tenant_id`/`database_name` (campos
obrigatórios em `CurrentUser`), e usa um cookie e um secret de assinatura próprios,
para nunca se misturar com uma sessão de tenant no mesmo navegador."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from fastapi import Depends, Request
from veloai_shared.exceptions import AuthenticationError
from veloai_shared.security.jwt import TokenError

from app.core.config import Settings, get_settings
from app.modules.admin.services.platform_admin_token_service import PlatformAdminTokenService

ADMIN_ACCESS_TOKEN_COOKIE_NAME = "admin_access_token"


@dataclass(frozen=True)
class CurrentPlatformAdmin:
    admin_id: uuid.UUID


def get_platform_admin_token_service(
    settings: Settings = Depends(get_settings),
) -> PlatformAdminTokenService:
    return PlatformAdminTokenService(settings)


async def get_current_platform_admin(
    request: Request,
    token_service: PlatformAdminTokenService = Depends(get_platform_admin_token_service),
) -> CurrentPlatformAdmin:
    token = request.cookies.get(ADMIN_ACCESS_TOKEN_COOKIE_NAME)
    if not token:
        raise AuthenticationError("Não autenticado.", code="NOT_AUTHENTICATED")

    try:
        claims = token_service.decode_token(token)
    except TokenError as exc:
        raise AuthenticationError(
            "Sessão inválida ou expirada.", code="SESSION_EXPIRED"
        ) from exc

    return CurrentPlatformAdmin(admin_id=claims.admin_id)
