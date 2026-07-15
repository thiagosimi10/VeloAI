"""Histórico de tentativas de login, conforme 08-CLIENTES.md (padrão de Timeline) e
29-SECURITY.md ("Login: Registro de tentativas, Detecção de força bruta")."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, UUIDPrimaryKeyMixin


class LoginHistory(TenantBase, UUIDPrimaryKeyMixin):
    __tablename__ = "login_history"

    user_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
