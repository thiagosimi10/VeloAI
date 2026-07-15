"""Fluxo de Caixa do tenant, conforme 05-BANCO-DE-DADOS.md (tabela `cash_flow`).
Livro-razão simples (sem status, sem link para outra tabela) — append-only, nunca
editado nem apagado (11-FINANCEIRO.md: "Nunca permitir exclusão de movimentações.
Sempre realizar estorno."), mesmo padrão de `StockMovement`/`TenantAuditLog`: só
`created_at`, sem `updated_at`/`deleted_at`. Um "estorno" é uma nova entrada com o tipo
oposto — não há coluna para linkar ao lançamento original."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, UUIDPrimaryKeyMixin


class CashFlowEntry(TenantBase, UUIDPrimaryKeyMixin):
    __tablename__ = "cash_flow"

    type: Mapped[str] = mapped_column(String(10), nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, server_default=func.current_date(), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
