"""Planos comerciais, conforme 31-BILLING.md."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.master.base import MasterBase, TimestampMixin, UUIDPrimaryKeyMixin


class Plan(MasterBase, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "plans"

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    trial_days: Mapped[int] = mapped_column(default=14, nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
