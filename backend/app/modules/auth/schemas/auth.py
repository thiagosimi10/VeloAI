"""DTOs do módulo de Autenticação, conforme 22-API-STANDARDS.md ("Toda entrada deverá
utilizar Pydantic v2.")."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator
from veloai_shared.validators import normalize_document


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=255)


class SignupRequest(BaseModel):
    """Cadastro self-service — cria a empresa (tenant), o usuário administrador e já
    autentica a pessoa, sem passar pelo fluxo admin-driven de `/admin/tenants`."""

    legal_name: str = Field(min_length=3, max_length=200)
    trade_name: str | None = Field(default=None, max_length=200)
    document: str = Field(min_length=11, max_length=18)
    admin_name: str = Field(min_length=3, max_length=200)
    admin_email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    # Honeypot: campo nunca preenchido por uma pessoa real, só por bots. Precisa chegar vazio.
    website: str = Field(default="", max_length=0)

    @field_validator("document")
    @classmethod
    def validate_document(cls, value: str) -> str:
        return normalize_document(value)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=255)
    new_password: str = Field(min_length=8, max_length=255)


class UpdateProfileRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=120)
    last_name: str | None = Field(default=None, max_length=120)


class MeResponse(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str | None
    role: str
    permissions: list[str]
    must_change_password: bool
    tenant_name: str
    avatar_url: str | None
