"""DTOs do módulo Billing, conforme 31-BILLING.md ("Billing Dashboard: Plano, Valor,
Próximo vencimento, Situação")."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class SubscriptionResponse(BaseModel):
    plan_name: str
    plan_price: Decimal
    status: str
    trial_ends_at: datetime | None
    current_period_ends_at: datetime | None
    days_remaining: int | None
