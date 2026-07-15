"""DTOs do módulo de Vendas — núcleo operacional, conforme 05-BANCO-DE-DADOS.md. Sem
`number` (diferente de toda outra entidade), sem vendedor, sem orçamento/parcelamento/
comissão (ver 12-VENDAS.md) — ficam para uma iteração futura."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.modules.sales.schemas.sale_item import SaleItemResponse

SaleStatus = Literal["open", "paid", "cancelled"]


class CreateSaleRequest(BaseModel):
    customer_id: uuid.UUID
    payment_method: str | None = Field(default=None, max_length=30)


class UpdateSaleRequest(BaseModel):
    discount: Decimal | None = Field(default=None, ge=0)
    payment_method: str | None = Field(default=None, max_length=30)


class SaleResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    status: SaleStatus
    payment_method: str | None
    discount: Decimal
    total: Decimal
    created_at: datetime
    items: list[SaleItemResponse] = []

    model_config = {"from_attributes": True}


class SaleFilterParams(BaseModel):
    customer_id: uuid.UUID | None = None
    status: SaleStatus | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
