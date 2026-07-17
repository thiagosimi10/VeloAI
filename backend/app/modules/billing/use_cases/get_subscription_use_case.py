"""Caso de uso: consultar a Assinatura + Plano do tenant atual, conforme
31-BILLING.md ("Billing Dashboard: Plano, Valor, Próximo vencimento, Situação")."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.database import get_master_session
from app.modules.billing.repositories.subscription_repository import SubscriptionRepository
from app.modules.billing.schemas.billing import SubscriptionResponse
from app.modules.billing.services.subscription_gate_service import resolve_subscription_status
from app.modules.billing.use_cases._helpers import to_subscription_response


class GetSubscriptionUseCase:
    async def execute(self, *, tenant_id: uuid.UUID) -> SubscriptionResponse:
        async with get_master_session() as session:
            repository = SubscriptionRepository(session)

            subscription = await repository.get_by_tenant_id(tenant_id)
            if subscription is None:
                raise NotFoundError(
                    "Assinatura não encontrada para este tenant.", code="SUBSCRIPTION_NOT_FOUND"
                )

            await resolve_subscription_status(repository, subscription)

            plan = await repository.get_plan(subscription.plan_id)
            if plan is None:
                raise NotFoundError("Plano não encontrado.", code="PLAN_NOT_FOUND")

        return to_subscription_response(subscription, plan)
