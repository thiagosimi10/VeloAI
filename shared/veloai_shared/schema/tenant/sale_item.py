"""Itens de uma Venda (sempre produto — 05-BANCO-DE-DADOS.md não tem `service_id` em
`sale_items`, diferente de `service_order_items`), conforme a tabela `sale_items`. Sem
soft delete e sem coluna `total` (calculado, nunca persistido) — item é removido de
verdade enquanto a venda ainda está `open`, sem valor histórico a preservar."""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, UUIDPrimaryKeyMixin


class SaleItem(TenantBase, UUIDPrimaryKeyMixin):
    __tablename__ = "sale_items"

    sale_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sales.id"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), nullable=False)

    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
