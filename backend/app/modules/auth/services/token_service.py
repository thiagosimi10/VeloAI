"""Emissão e decodificação dos tokens JWT específicos do VeloAI (access/refresh),
conforme 02-ARQUITETURA.md ("JWT, Refresh Token, Tempo curto para Access Token, Refresh
Token renovável") e 16-BACKEND-ARCHITECTURE.md.

O `access_token` embute `tenant_id` e `database_name` para que requisições autenticadas
resolvam a conexão do tenant sem precisar consultar o Banco Master a cada requisição —
apenas o login (que ainda não tem token) consulta o índice de roteamento."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from veloai_shared.security.jwt import TokenInvalidError, create_token, decode_token

from app.core.config import Settings


@dataclass(frozen=True)
class AccessTokenClaims:
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    database_name: str
    role: str


@dataclass(frozen=True)
class RefreshTokenClaims:
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    database_name: str
    jti: str


class TokenService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def issue_access_token(
        self, *, user_id: uuid.UUID, tenant_id: uuid.UUID, database_name: str, role: str
    ) -> str:
        return create_token(
            subject=str(user_id),
            secret=self._settings.jwt_secret,
            expires_delta=timedelta(minutes=self._settings.jwt_access_token_expire_minutes),
            extra_claims={
                "type": "access",
                "tenant_id": str(tenant_id),
                "database_name": database_name,
                "role": role,
            },
        )

    def issue_refresh_token(
        self, *, user_id: uuid.UUID, tenant_id: uuid.UUID, database_name: str
    ) -> str:
        return create_token(
            subject=str(user_id),
            secret=self._settings.jwt_refresh_secret,
            expires_delta=timedelta(days=self._settings.jwt_refresh_token_expire_days),
            extra_claims={
                "type": "refresh",
                "tenant_id": str(tenant_id),
                "database_name": database_name,
            },
        )

    def decode_access_token(self, token: str) -> AccessTokenClaims:
        payload = decode_token(token, secret=self._settings.jwt_secret)
        self._assert_type(payload, "access")
        return AccessTokenClaims(
            user_id=uuid.UUID(payload["sub"]),
            tenant_id=uuid.UUID(payload["tenant_id"]),
            database_name=payload["database_name"],
            role=payload["role"],
        )

    def decode_refresh_token(self, token: str) -> RefreshTokenClaims:
        payload = decode_token(token, secret=self._settings.jwt_refresh_secret)
        self._assert_type(payload, "refresh")
        return RefreshTokenClaims(
            user_id=uuid.UUID(payload["sub"]),
            tenant_id=uuid.UUID(payload["tenant_id"]),
            database_name=payload["database_name"],
            jti=payload["jti"],
        )

    @staticmethod
    def hash_refresh_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _assert_type(payload: dict[str, Any], expected: str) -> None:
        if payload.get("type") != expected:
            raise TokenInvalidError(f"Esperado token do tipo '{expected}'.")
