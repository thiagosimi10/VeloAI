"""Opções de ciclo de cobrança do plano VeloAI Professional, conforme combinado com o
usuário: mensal sem desconto, semestral e anual com desconto por compromisso.

Config estática (não é tabela de banco) — o `Plan` em `shared/veloai_shared/schema/
master/plan.py` continua sendo só o produto único usado para o trial; o ciclo/preço
escolhido no checkout vive em `Subscription.billing_cycle`, não em `Plan`."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PlanTier:
    cycle: str
    label: str
    months: int
    monthly_price: Decimal

    @property
    def total_price(self) -> Decimal:
        return self.monthly_price * self.months


PLAN_TIERS: list[PlanTier] = [
    PlanTier(cycle="MONTHLY", label="Mensal", months=1, monthly_price=Decimal("129.90")),
    PlanTier(cycle="SEMIANNUALLY", label="Semestral", months=6, monthly_price=Decimal("109.00")),
    PlanTier(cycle="YEARLY", label="Anual", months=12, monthly_price=Decimal("99.00")),
]


def get_plan_tier(cycle: str) -> PlanTier | None:
    return next((tier for tier in PLAN_TIERS if tier.cycle == cycle), None)
