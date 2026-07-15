"""Refresh Tokens do tenant — permitem rotação e revogação de sessões, conforme
16-BACKEND-ARCHITECTURE.md ("Autenticação: JWT, Refresh Token, Rotação automática,
Blacklist...") e 29-SECURITY.md ("Revogação de Sessões").

Armazena apenas o hash SHA-256 do token, nunca o valor original — mesmo sendo um valor
opaco e de uso único, tratamos como segredo em repouso."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, UUIDPrimaryKeyMixin


class RefreshToken(TenantBase, UUIDPrimaryKeyMixin):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
