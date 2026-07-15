"""Ordens de Serviço do tenant, conforme 05-BANCO-DE-DADOS.md (tabela
`service_orders`). Esta fase cobre o núcleo operacional (cadastro, itens, fluxo de
status, consumo de estoque na conclusão) — agenda, financeiro, fiscal, anexos/fotos/
assinatura, checklist e PDF (ver 10-ORDEM-DE-SERVICO.md) ficam para uma iteração
futura."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, TimestampMixin, UUIDPrimaryKeyMixin


class ServiceOrder(TenantBase, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "service_orders"

    number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"), nullable=False)
    technician_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)

    equipment: Mapped[str | None] = mapped_column(String(200), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    problem: Mapped[str | None] = mapped_column(Text, nullable=True)
    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)
    solution: Mapped[str | None] = mapped_column(Text, nullable=True)

    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
