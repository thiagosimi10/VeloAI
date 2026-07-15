"""DTOs do módulo de Fornecedores — mesmos campos de Clientes, conforme
05-BANCO-DE-DADOS.md ("Mesmo padrão dos clientes")."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator
from veloai_shared.validators import normalize_document

SupplierType = Literal["PF", "PJ"]


class CreateSupplierRequest(BaseModel):
    type: SupplierType
    name: str = Field(min_length=3, max_length=200)
    document: str = Field(min_length=11, max_length=18)
    state_registration: str | None = Field(default=None, max_length=30)
    municipal_registration: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    mobile: str | None = Field(default=None, max_length=30)
    whatsapp: str | None = Field(default=None, max_length=30)
    zipcode: str | None = Field(default=None, max_length=10)
    street: str | None = Field(default=None, max_length=200)
    number: str | None = Field(default=None, max_length=20)
    district: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=2)
    country: str = Field(default="Brasil", max_length=60)
    notes: str | None = None

    @field_validator("document")
    @classmethod
    def validate_document(cls, value: str) -> str:
        return normalize_document(value)


class UpdateSupplierRequest(BaseModel):
    type: SupplierType | None = None
    name: str | None = Field(default=None, min_length=3, max_length=200)
    state_registration: str | None = Field(default=None, max_length=30)
    municipal_registration: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    mobile: str | None = Field(default=None, max_length=30)
    whatsapp: str | None = Field(default=None, max_length=30)
    zipcode: str | None = Field(default=None, max_length=10)
    street: str | None = Field(default=None, max_length=200)
    number: str | None = Field(default=None, max_length=20)
    district: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=2)
    country: str | None = Field(default=None, max_length=60)
    notes: str | None = None
    active: bool | None = None


class SupplierResponse(BaseModel):
    id: uuid.UUID
    code: str
    type: SupplierType
    name: str
    document: str
    state_registration: str | None
    municipal_registration: str | None
    email: str | None
    phone: str | None
    mobile: str | None
    whatsapp: str | None
    zipcode: str | None
    street: str | None
    number: str | None
    district: str | None
    city: str | None
    state: str | None
    country: str
    notes: str | None
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SupplierFilterParams(BaseModel):
    search: str | None = None
    sort: Literal["name", "code", "created_at"] = "name"
    order: Literal["asc", "desc"] = "asc"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
