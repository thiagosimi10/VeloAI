"""DTOs de Contas a Pagar — espelho de `account_receivable.py`, trocando `customer_id`
por `supplier_id`."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, computed_field

AccountPayableStatus = Literal["pending", "paid", "cancelled"]


class CreateAccountPayableRequest(BaseModel):
    supplier_id: uuid.UUID
    due_date: date
    amount: Decimal = Field(gt=0)


class UpdateAccountPayableRequest(BaseModel):
    due_date: date | None = None
    amount: Decimal | None = Field(default=None, gt=0)


class AccountPayableResponse(BaseModel):
    id: uuid.UUID
    supplier_id: uuid.UUID
    due_date: date
    amount: Decimal
    status: AccountPayableStatus
    payment_date: date | None

    model_config = {"from_attributes": True}

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_overdue(self) -> bool:
        return self.status == "pending" and self.due_date < date.today()


class AccountPayableFilterParams(BaseModel):
    supplier_id: uuid.UUID | None = None
    status: AccountPayableStatus | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
