"""Registro de Tenants (empresas), conforme 04-MULTI-TENANCY.md e
19-PROVISIONING-SERVICE.md. Nunca armazena senha do banco em texto puro."""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.master.base import MasterBase, TimestampMixin, UUIDPrimaryKeyMixin


class TenantStatus(str, enum.Enum):
    PROVISIONING = "PROVISIONING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class Tenant(MasterBase, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "tenants"

    legal_name: Mapped[str] = mapped_column(String(200), nullable=False)
    trade_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    document: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    database_name: Mapped[str] = mapped_column(String(63), unique=True, nullable=False)
    database_host: Mapped[str] = mapped_column(String(255), nullable=False)
    database_port: Mapped[int] = mapped_column(nullable=False)

    plan_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("plans.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default=TenantStatus.PROVISIONING.value, nullable=False
    )
