"""DTOs de Fluxo de Caixa, conforme a tabela `cash_flow` (05-BANCO-DE-DADOS.md) —
livro-razão simples, sem status nem link para outra tabela. Sem edição/exclusão — só
criação e listagem (11-FINANCEIRO.md: "Nunca permitir exclusão de movimentações. Sempre
realizar estorno." — estornar é lançar uma nova entrada com o tipo oposto)."""

from __future__ import annotations

import uuid
import datetime as dt
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

CashFlowEntryType = Literal["in", "out"]


class CreateCashFlowEntryRequest(BaseModel):
    type: CashFlowEntryType
    category: str = Field(min_length=1, max_length=60)
    description: str | None = Field(default=None, max_length=255)
    amount: Decimal = Field(gt=0)
    date: dt.date | None = None


class CashFlowEntryResponse(BaseModel):
    id: uuid.UUID
    type: CashFlowEntryType
    category: str
    description: str | None
    amount: Decimal
    date: dt.date
    created_at: dt.datetime

    model_config = {"from_attributes": True}


class CashFlowFilterParams(BaseModel):
    type: CashFlowEntryType | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
