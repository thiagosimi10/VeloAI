"""DTOs de itens de Ordem de Serviço (produto ou serviço), conforme
05-BANCO-DE-DADOS.md (tabela `service_order_items`)."""

from __future__ import annotations

import uuid
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


class AddServiceOrderItemRequest(BaseModel):
    product_id: uuid.UUID | None = None
    service_id: uuid.UUID | None = None
    quantity: int = Field(default=1, gt=0)
    unit_price: Decimal | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _validate_exactly_one_reference(self) -> "AddServiceOrderItemRequest":
        if (self.product_id is None) == (self.service_id is None):
            raise ValueError(
                "Informe exatamente um item: product_id OU service_id (nunca os dois, "
                "nunca nenhum)."
            )
        return self


class ServiceOrderItemResponse(BaseModel):
    id: uuid.UUID
    service_order_id: uuid.UUID
    product_id: uuid.UUID | None
    service_id: uuid.UUID | None
    quantity: int
    unit_price: Decimal
    total: Decimal

    model_config = {"from_attributes": True}
