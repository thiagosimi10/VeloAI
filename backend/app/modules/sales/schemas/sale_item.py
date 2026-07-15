"""DTOs de itens de Venda (sempre produto — 05-BANCO-DE-DADOS.md não tem `service_id`
em `sale_items`), conforme a tabela `sale_items`."""

from __future__ import annotations

import uuid
from decimal import Decimal

from pydantic import BaseModel, Field, computed_field


class AddSaleItemRequest(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(default=1, gt=0)
    unit_price: Decimal | None = Field(default=None, ge=0)


class SaleItemResponse(BaseModel):
    id: uuid.UUID
    sale_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    unit_price: Decimal

    model_config = {"from_attributes": True}

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total(self) -> Decimal:
        """Nunca persistido — `sale_items` não tem coluna `total` (diferente de
        `service_order_items`), calculado sempre na resposta."""

        return (self.quantity * self.unit_price).quantize(Decimal("0.01"))
