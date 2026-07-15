"""Contas a Receber do tenant, conforme 05-BANCO-DE-DADOS.md (tabela
`accounts_receivable`). Esta fase cobre o núcleo operacional (cadastro, recebimento,
cancelamento) — juros, multa, desconto, recebimento parcial, categoria, centro de
custo, documento, origem e forma de pagamento (ver 11-FINANCEIRO.md) ficam para uma
iteração futura. Nunca excluída (`11-FINANCEIRO.md`: "Nunca excluir lançamentos
financeiros. Sempre utilizar estorno.") — por isso não há `deleted_at` sendo utilizado
por nenhum caso de uso, mesmo com `TimestampMixin`."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, TimestampMixin, UUIDPrimaryKeyMixin


class AccountReceivable(TenantBase, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "accounts_receivable"

    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
