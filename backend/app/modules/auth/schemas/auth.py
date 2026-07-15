"""DTOs do módulo de Autenticação, conforme 22-API-STANDARDS.md ("Toda entrada deverá
utilizar Pydantic v2.")."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=255)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=255)
    new_password: str = Field(min_length=8, max_length=255)


class MeResponse(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str | None
    role: str
    permissions: list[str]
    must_change_password: bool
