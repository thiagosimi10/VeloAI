"""Categorias do tenant, conforme 05-BANCO-DE-DADOS.md (tabela `categories`).
Organiza produtos e serviços — entidade simples, sem código sequencial nem documento
(mesmo padrão de `TenantRole`, ver `veloai_shared/schema/tenant/rbac.py`)."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, TimestampMixin, UUIDPrimaryKeyMixin


class Category(TenantBase, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
