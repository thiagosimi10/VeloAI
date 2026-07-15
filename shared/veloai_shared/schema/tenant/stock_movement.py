"""Histórico de movimentações de estoque, conforme 05-BANCO-DE-DADOS.md (tabela
`stock_movements`). Append-only — nunca editada nem apagada ("Movimentações nunca
poderão ser apagadas", 09-PRODUTOS.md), mesmo padrão de `TenantAuditLog`
(`veloai_shared/schema/tenant/audit_log.py`): só `created_at`, sem `updated_at`/
`deleted_at`."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, UUIDPrimaryKeyMixin


class StockMovement(TenantBase, UUIDPrimaryKeyMixin):
    __tablename__ = "stock_movements"

    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    movement: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    previous_stock: Mapped[int] = mapped_column(nullable=False)
    current_stock: Mapped[int] = mapped_column(nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
