"""Caso de uso: listar as opções de ciclo de cobrança disponíveis para assinatura."""

from __future__ import annotations

from app.modules.billing.pricing import PLAN_TIERS
from app.modules.billing.schemas.billing import PlanTierResponse


class ListPlanTiersUseCase:
    async def execute(self) -> list[PlanTierResponse]:
        return [
            PlanTierResponse(
                cycle=tier.cycle,
                label=tier.label,
                months=tier.months,
                monthly_price=tier.monthly_price,
                total_price=tier.total_price,
            )
            for tier in PLAN_TIERS
        ]
