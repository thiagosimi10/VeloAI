"""Itens de uma Ordem de Serviço (produto ou serviço), conforme 05-BANCO-DE-DADOS.md
(tabela `service_order_items`). Sem soft delete — item é removido de verdade quando a
regra de negócio permitir (nunca depois da OS concluída/cancelada); diferente de
`StockMovement`, não é, em si, um histórico a preservar."""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, UUIDPrimaryKeyMixin


class ServiceOrderItem(TenantBase, UUIDPrimaryKeyMixin):
    __tablename__ = "service_order_items"

    service_order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("service_orders.id"), nullable=False
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("products.id"), nullable=True)
    service_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("services.id"), nullable=True)

    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
