"""DTOs de movimentação de estoque, conforme 05-BANCO-DE-DADOS.md (tabela
`stock_movements`) e 09-PRODUTOS.md ("Alteração manual de estoque deverá registrar
motivo")."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

StockMovementType = Literal["in", "out", "adjustment"]


class CreateStockMovementRequest(BaseModel):
    movement: StockMovementType
    quantity: int = Field(
        ge=0,
        description=(
            "Para 'in'/'out', a magnitude do delta a aplicar (deve ser maior que zero). "
            "Para 'adjustment', o novo valor absoluto de estoque (contagem de inventário "
            "— pode ser zero, quando a contagem revela que o produto está esgotado)."
        ),
    )
    reason: str = Field(min_length=3, max_length=255)

    @model_validator(mode="after")
    def _validate_quantity_for_movement_type(self) -> "CreateStockMovementRequest":
        if self.movement in ("in", "out") and self.quantity == 0:
            raise ValueError(
                "quantity deve ser maior que zero para movimentações do tipo 'in'/'out'."
            )
        return self


class StockMovementResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    movement: StockMovementType
    quantity: int
    previous_stock: int
    current_stock: int
    reason: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StockMovementFilterParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
