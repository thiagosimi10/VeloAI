"""DTOs do módulo Admin (Painel Administrativo, Fase 18), conforme 22-API-STANDARDS.md
("Toda entrada deverá utilizar Pydantic v2.")."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=255)


class ChangeAdminPasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=255)
    new_password: str = Field(min_length=8, max_length=255)


class PlatformAdminResponse(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str | None
    must_change_password: bool


class TenantOverviewItem(BaseModel):
    tenant_id: uuid.UUID
    legal_name: str
    document: str
    status: str
    plan_name: str | None
    subscription_status: str | None
    trial_ends_at: datetime | None


class AdminSummaryResponse(BaseModel):
    total_tenants: int
    trial_count: int
    active_count: int
    pending_payment_count: int
    overdue_count: int
    suspended_count: int
    canceled_count: int
    expired_count: int
    estimated_mrr: Decimal


class AuditLogEntryResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    action: str
    resource: str
    before: dict[str, Any] | None
    after: dict[str, Any] | None
    created_at: datetime
