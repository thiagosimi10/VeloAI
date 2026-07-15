"""Vendas do tenant, conforme 05-BANCO-DE-DADOS.md (tabela `sales`). Esta fase cobre o
núcleo operacional (cadastro, itens de produto, desconto, forma de pagamento, consumo de
estoque na conclusão) — orçamentos, venda de serviços/mista, parcelamento, comissões e
integração fiscal/financeira (ver 12-VENDAS.md) ficam para uma iteração futura. Nunca
excluída (`12-VENDAS.md`: "Nunca excluir vendas. Sempre cancelar.") — por isso não há
`deleted_at` sendo utilizado por nenhum caso de uso, mesmo com `TimestampMixin`."""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, TimestampMixin, UUIDPrimaryKeyMixin


class Sale(TenantBase, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "sales"

    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)
    payment_method: Mapped[str | None] = mapped_column(String(30), nullable=True)

    discount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
