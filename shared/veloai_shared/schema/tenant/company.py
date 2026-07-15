"""Perfil da própria empresa dentro do seu banco de tenant, conforme
05-BANCO-DE-DADOS.md (tabela `companies`)."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, TimestampMixin, UUIDPrimaryKeyMixin


class Company(TenantBase, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "companies"

    legal_name: Mapped[str] = mapped_column(String(200), nullable=False)
    trade_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    document: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    timezone: Mapped[str] = mapped_column(String(60), default="America/Sao_Paulo", nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="BRL", nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
