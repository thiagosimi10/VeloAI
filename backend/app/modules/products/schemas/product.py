"""DTOs do módulo de Produtos — campos conforme 05-BANCO-DE-DADOS.md. Campos fiscais,
imagens, anexos e histórico de movimentações (Fase 7) ficam para uma iteração futura."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, computed_field


class CreateProductRequest(BaseModel):
    category_id: uuid.UUID | None = None
    supplier_id: uuid.UUID | None = None
    sku: str = Field(min_length=1, max_length=60)
    barcode: str | None = Field(default=None, max_length=60)
    name: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    cost_price: Decimal = Field(ge=0)
    sale_price: Decimal = Field(ge=0)
    stock: int = Field(default=0, ge=0)
    minimum_stock: int | None = Field(default=None, ge=0)
    maximum_stock: int | None = Field(default=None, ge=0)
    unit: str = Field(default="UN", max_length=10)
    weight: Decimal | None = Field(default=None, ge=0)


class UpdateProductRequest(BaseModel):
    category_id: uuid.UUID | None = None
    supplier_id: uuid.UUID | None = None
    barcode: str | None = Field(default=None, max_length=60)
    name: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    cost_price: Decimal | None = Field(default=None, ge=0)
    sale_price: Decimal | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    minimum_stock: int | None = Field(default=None, ge=0)
    maximum_stock: int | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=10)
    weight: Decimal | None = Field(default=None, ge=0)
    active: bool | None = None


class ProductResponse(BaseModel):
    id: uuid.UUID
    category_id: uuid.UUID | None
    supplier_id: uuid.UUID | None
    sku: str
    barcode: str | None
    name: str
    description: str | None
    cost_price: Decimal
    sale_price: Decimal
    stock: int
    minimum_stock: int | None
    maximum_stock: int | None
    unit: str
    weight: Decimal | None
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @computed_field  # type: ignore[prop-decorator]
    @property
    def margin(self) -> Decimal:
        """Lucro bruto unitário (`sale_price - cost_price`). Calculado na resposta,
        nunca persistido, conforme 09-PRODUTOS.md ("Margem deverá ser calculada
        automaticamente")."""

        return self.sale_price - self.cost_price

    @computed_field  # type: ignore[prop-decorator]
    @property
    def margin_percentage(self) -> Decimal | None:
        if self.cost_price == 0:
            return None
        return round((self.margin / self.cost_price) * 100, 2)


class ProductFilterParams(BaseModel):
    search: str | None = None
    category_id: uuid.UUID | None = None
    supplier_id: uuid.UUID | None = None
    sort: Literal["name", "sku", "created_at"] = "name"
    order: Literal["asc", "desc"] = "asc"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
