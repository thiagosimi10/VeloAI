"""DTOs do módulo de Configurações da Empresa (`companies`, uma linha por tenant), conforme
22-API-STANDARDS.md ("Toda entrada deverá utilizar Pydantic v2."). `document` nunca é
editável por aqui — é definido apenas no cadastro/provisionamento."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UpdateCompanyRequest(BaseModel):
    legal_name: str = Field(min_length=3, max_length=200)
    trade_name: str | None = Field(default=None, max_length=200)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)


class CompanyResponse(BaseModel):
    id: uuid.UUID
    legal_name: str
    trade_name: str | None
    document: str
    email: str | None
    phone: str | None
    timezone: str
    currency: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
