"""DTOs de entrada/saída do Provisioning Service, conforme 22-API-STANDARDS.md
("Toda entrada deverá utilizar Pydantic v2. Nunca validar manualmente nas rotas")."""

from __future__ import annotations

import re
import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator


class CreateTenantRequest(BaseModel):
    legal_name: str = Field(min_length=3, max_length=200)
    trade_name: str | None = Field(default=None, max_length=200)
    document: str = Field(min_length=11, max_length=18)
    admin_name: str = Field(min_length=3, max_length=200)
    admin_email: EmailStr

    @field_validator("document")
    @classmethod
    def validate_document(cls, value: str) -> str:
        digits = re.sub(r"\D", "", value)
        if len(digits) not in (11, 14):
            raise ValueError("Documento deve ser um CPF (11 dígitos) ou CNPJ (14 dígitos).")
        return digits


class TenantResponse(BaseModel):
    tenant_id: uuid.UUID
    legal_name: str
    document: str
    database_name: str
    status: str


class TenantAdminCredentials(BaseModel):
    """Retornado apenas na criação do tenant, para que o e-mail de boas-vindas seja
    disparado (Fase de Notificações — fora do escopo desta fundação). Nunca é
    persistido em texto puro."""

    admin_email: EmailStr
    temporary_password: str


class TenantProvisionedResponse(TenantResponse):
    admin: TenantAdminCredentials
