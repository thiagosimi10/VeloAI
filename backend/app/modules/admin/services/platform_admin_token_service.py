"""Emissão e decodificação do token de sessão de Platform Admin, conforme
34-MASTER-PLAN.md (Fase 18). Deliberadamente separado de `auth/services/
token_service.py::TokenService` — aquele exige `tenant_id`/`database_name` (claims
obrigatórias), que um operador da plataforma não tem. Assina com um secret próprio
(`Settings.platform_admin_jwt_secret`) para isolar essa confiança da de tokens de
tenant. Só access token — sem refresh nesta fase (login de novo quando expirar)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import timedelta

from veloai_shared.security.jwt import TokenInvalidError, create_token, decode_token

from app.core.config import Settings


@dataclass(frozen=True)
class PlatformAdminTokenClaims:
    admin_id: uuid.UUID


class PlatformAdminTokenService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def issue_token(self, *, admin_id: uuid.UUID) -> str:
        return create_token(
            subject=str(admin_id),
            secret=self._settings.platform_admin_jwt_secret,
            expires_delta=timedelta(minutes=self._settings.platform_admin_token_expire_minutes),
            extra_claims={"type": "platform_admin"},
        )

    def decode_token(self, token: str) -> PlatformAdminTokenClaims:
        payload = decode_token(token, secret=self._settings.platform_admin_jwt_secret)
        if payload.get("type") != "platform_admin":
            raise TokenInvalidError("Esperado token do tipo 'platform_admin'.")
        return PlatformAdminTokenClaims(admin_id=uuid.UUID(payload["sub"]))
