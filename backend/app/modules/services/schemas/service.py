"""DTOs do módulo de Serviços, conforme 05-BANCO-DE-DADOS.md e 06-MODULOS.md
("Categoria" como responsabilidade do módulo)."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class CreateServiceRequest(BaseModel):
    category_id: uuid.UUID | None = None
    name: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    estimated_time: int | None = Field(default=None, ge=0)
    price: Decimal = Field(ge=0)


class UpdateServiceRequest(BaseModel):
    category_id: uuid.UUID | None = None
    name: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    estimated_time: int | None = Field(default=None, ge=0)
    price: Decimal | None = Field(default=None, ge=0)
    active: bool | None = None


class ServiceResponse(BaseModel):
    id: uuid.UUID
    category_id: uuid.UUID | None
    code: str
    name: str
    description: str | None
    estimated_time: int | None
    price: Decimal
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ServiceFilterParams(BaseModel):
    search: str | None = None
    category_id: uuid.UUID | None = None
    sort: Literal["name", "code", "created_at"] = "name"
    order: Literal["asc", "desc"] = "asc"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
