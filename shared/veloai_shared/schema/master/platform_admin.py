"""Operadores da própria VeloAI (equipe interna), conforme 31-BILLING.md ("Admin
Master") e 34-MASTER-PLAN.md (Fase 18). Nunca um usuário de tenant — vive
exclusivamente no Banco Master, sem `tenant_id`, e nunca é seedado pelo Provisioning
por tenant (bootstrap único via `scripts/seed_master.py`)."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.master.base import MasterBase, TimestampMixin, UUIDPrimaryKeyMixin


class PlatformAdmin(MasterBase, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "platform_admins"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
    force_password_change: Mapped[bool] = mapped_column(default=True, nullable=False)
