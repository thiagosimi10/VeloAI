"""DTOs do módulo de Ordens de Serviço — núcleo operacional, conforme
05-BANCO-DE-DADOS.md. Campos fiscais, agenda, financeiro, anexos/fotos/assinatura,
checklist e PDF (ver 10-ORDEM-DE-SERVICO.md) ficam para uma iteração futura."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.modules.service_orders.schemas.service_order_item import ServiceOrderItemResponse

ServiceOrderStatus = Literal["open", "in_progress", "completed", "cancelled"]


class CreateServiceOrderRequest(BaseModel):
    customer_id: uuid.UUID
    technician_id: uuid.UUID | None = None
    equipment: str | None = Field(default=None, max_length=200)
    serial_number: str | None = Field(default=None, max_length=100)
    problem: str | None = None


class UpdateServiceOrderRequest(BaseModel):
    technician_id: uuid.UUID | None = None
    equipment: str | None = Field(default=None, max_length=200)
    serial_number: str | None = Field(default=None, max_length=100)
    problem: str | None = None
    diagnosis: str | None = None
    solution: str | None = None


class CloseServiceOrderRequest(BaseModel):
    technician_id: uuid.UUID | None = None
    solution: str | None = None


class ServiceOrderResponse(BaseModel):
    id: uuid.UUID
    number: str
    customer_id: uuid.UUID
    technician_id: uuid.UUID | None
    status: ServiceOrderStatus
    equipment: str | None
    serial_number: str | None
    problem: str | None
    diagnosis: str | None
    solution: str | None
    total: Decimal
    opened_at: datetime
    finished_at: datetime | None
    items: list[ServiceOrderItemResponse] = []

    model_config = {"from_attributes": True}


class ServiceOrderFilterParams(BaseModel):
    search: str | None = None
    customer_id: uuid.UUID | None = None
    technician_id: uuid.UUID | None = None
    status: ServiceOrderStatus | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
