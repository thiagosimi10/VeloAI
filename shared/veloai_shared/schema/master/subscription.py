"""Assinaturas, conforme 31-BILLING.md ("Estados da Assinatura: TRIAL, ACTIVE,
PENDING_PAYMENT, OVERDUE, SUSPENDED, CANCELED, EXPIRED")."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.master.base import MasterBase, TimestampMixin, UUIDPrimaryKeyMixin


class SubscriptionStatus(str, enum.Enum):
    TRIAL = "TRIAL"
    ACTIVE = "ACTIVE"
    PENDING_PAYMENT = "PENDING_PAYMENT"
    OVERDUE = "OVERDUE"
    SUSPENDED = "SUSPENDED"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"


class Subscription(MasterBase, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "subscriptions"

    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("plans.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=SubscriptionStatus.TRIAL.value, nullable=False
    )
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
