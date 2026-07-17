"""Caso de uso: cancelar a própria Assinatura, conforme 31-BILLING.md ("Cancelamento
quando desejar"). Sem gateway de pagamento — cancelamento é uma decisão do próprio
tenant, não depende de nenhuma confirmação externa."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import ConflictError, NotFoundError
from veloai_shared.schema.master import SubscriptionStatus

from app.core.database import get_master_session
from app.modules.billing.repositories.subscription_repository import SubscriptionRepository
from app.modules.billing.schemas.billing import SubscriptionResponse
from app.modules.billing.use_cases._helpers import to_subscription_response


class CancelSubscriptionUseCase:
    async def execute(self, *, tenant_id: uuid.UUID) -> SubscriptionResponse:
        async with get_master_session() as session:
            repository = SubscriptionRepository(session)

            subscription = await repository.get_by_tenant_id(tenant_id)
            if subscription is None:
                raise NotFoundError(
                    "Assinatura não encontrada para este tenant.", code="SUBSCRIPTION_NOT_FOUND"
                )

            if subscription.status == SubscriptionStatus.CANCELED.value:
                raise ConflictError(
                    "Assinatura já está cancelada.", code="SUBSCRIPTION_ALREADY_CANCELED"
                )

            before_status = subscription.status
            await repository.update_status(subscription, SubscriptionStatus.CANCELED)
            await repository.add_audit_log(
                tenant_id=tenant_id,
                action="SUBSCRIPTION_CANCELED",
                resource="subscriptions",
                before={"status": before_status},
                after={"status": SubscriptionStatus.CANCELED.value},
            )
            await repository.commit()

            plan = await repository.get_plan(subscription.plan_id)
            if plan is None:
                raise NotFoundError("Plano não encontrado.", code="PLAN_NOT_FOUND")

        return to_subscription_response(subscription, plan)
