"""DTOs de Contas a Receber — núcleo operacional, conforme 05-BANCO-DE-DADOS.md. Juros,
multa, desconto, valor recebido parcial, categoria, centro de custo, documento, origem
e forma de pagamento (ver 11-FINANCEIRO.md) ficam para uma iteração futura."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, computed_field

AccountReceivableStatus = Literal["pending", "received", "cancelled"]


class CreateAccountReceivableRequest(BaseModel):
    customer_id: uuid.UUID
    due_date: date
    amount: Decimal = Field(gt=0)


class UpdateAccountReceivableRequest(BaseModel):
    due_date: date | None = None
    amount: Decimal | None = Field(default=None, gt=0)


class AccountReceivableResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    due_date: date
    amount: Decimal
    status: AccountReceivableStatus
    payment_date: date | None

    model_config = {"from_attributes": True}

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_overdue(self) -> bool:
        """Não é um status armazenado (exigiria um job agendado para transitar
        automaticamente) — calculado na resposta a partir da data atual."""

        return self.status == "pending" and self.due_date < date.today()


class AccountReceivableFilterParams(BaseModel):
    customer_id: uuid.UUID | None = None
    status: AccountReceivableStatus | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
