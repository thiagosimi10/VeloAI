"""DTOs do módulo de Usuários — apenas leitura nesta fase, conforme
05-BANCO-DE-DADOS.md (tabela `users`)."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str | None
    email: str
    active: bool

    model_config = {"from_attributes": True}


class UserFilterParams(BaseModel):
    search: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
