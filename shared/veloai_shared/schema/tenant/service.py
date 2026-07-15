"""Serviços do tenant, conforme 05-BANCO-DE-DADOS.md (tabela `services`). Vínculo com
Ordens de Serviço (Fase 8), MCP Tools e eventos de domínio ficam para uma iteração
futura."""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, TimestampMixin, UUIDPrimaryKeyMixin


class Service(TenantBase, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "services"

    category_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )

    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    estimated_time: Mapped[int | None] = mapped_column(nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    active: Mapped[bool] = mapped_column(default=True, nullable=False)
