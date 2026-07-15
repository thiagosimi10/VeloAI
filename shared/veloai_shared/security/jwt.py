"""Emissão e validação de tokens JWT, conforme 02-ARQUITETURA.md ("Autenticação: JWT,
Refresh Token") e 16-BACKEND-ARCHITECTURE.md ("Rotação automática, Blacklist,
Expiração").

Este módulo é intencionalmente genérico: não conhece "access" ou "refresh" — quem chama
decide o segredo, o algoritmo, o tempo de expiração e quais claims extras incluir (ex.:
`tenant_id`, `role`, `type`). Isso evita acoplar o utilitário compartilhado às regras de
negócio específicas do VeloAI."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

DEFAULT_ALGORITHM = "HS256"


class TokenError(Exception):
    """Erro base ao emitir ou validar um token JWT."""


class TokenExpiredError(TokenError):
    """O token é válido mas já expirou."""


class TokenInvalidError(TokenError):
    """O token é malformado, tem assinatura inválida ou claims incompatíveis."""


def create_token(
    *,
    subject: str,
    secret: str,
    expires_delta: timedelta,
    algorithm: str = DEFAULT_ALGORITHM,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Cria um JWT assinado. `subject` vira a claim `sub`; um `jti` único é sempre
    incluído para permitir revogação individual (ex.: refresh tokens)."""

    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_token(token: str, *, secret: str, algorithm: str = DEFAULT_ALGORITHM) -> dict[str, Any]:
    """Decodifica e valida um JWT. Levanta `TokenExpiredError`/`TokenInvalidError` em
    vez de deixar vazar exceções da biblioteca `PyJWT` para as camadas superiores."""

    try:
        return jwt.decode(token, secret, algorithms=[algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredError("Token expirado.") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenInvalidError("Token inválido.") from exc
