"""Contas a Pagar do tenant, conforme 05-BANCO-DE-DADOS.md (tabela `accounts_payable`).
Espelho de `AccountReceivable`, trocando `customer_id` por `supplier_id` — mesmas
ressalvas de escopo e de regra de negócio (nunca excluída)."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, TimestampMixin, UUIDPrimaryKeyMixin


class AccountPayable(TenantBase, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "accounts_payable"

    supplier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
