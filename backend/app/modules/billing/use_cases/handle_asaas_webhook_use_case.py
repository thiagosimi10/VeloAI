"""Caso de uso: processar eventos de Checkout recebidos via webhook da Asaas — único
lugar que confirma um pagamento de verdade (nunca o retorno do navegador no
`callback.successUrl`, que o usuário pode manipular). Conforme `docs/31-BILLING.md`.

Escopo desta fase: só `CHECKOUT_PAID` muda o estado da Assinatura (ativa o ciclo pago).
`CHECKOUT_CREATED`/`CHECKOUT_CANCELED`/`CHECKOUT_EXPIRED` apenas geram auditoria — um
checkout abandonado não deve travar nem destravar o tenant, que continua com o status
que já tinha antes de começar o checkout."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from veloai_shared.schema.master import SubscriptionStatus

from app.core.database import get_master_session
from app.modules.billing.pricing import get_plan_tier
from app.modules.billing.repositories.subscription_repository import SubscriptionRepository
from app.modules.billing.use_cases._helpers import add_months

_STATUS_CHANGING_EVENT = "CHECKOUT_PAID"
_AUDITED_EVENTS = {"CHECKOUT_CREATED", "CHECKOUT_PAID", "CHECKOUT_CANCELED", "CHECKOUT_EXPIRED"}


class HandleAsaasWebhookUseCase:
    async def execute(self, payload: dict[str, Any]) -> None:
        event = payload.get("event")
        if event not in _AUDITED_EVENTS:
            return

        checkout = payload.get("checkout") or {}
        external_reference = checkout.get("externalReference")
        if not external_reference:
            return

        try:
            tenant_id = uuid.UUID(external_reference)
        except ValueError:
            return

        async with get_master_session() as session:
            repository = SubscriptionRepository(session)
            subscription = await repository.get_by_tenant_id(tenant_id)
            if subscription is None:
                return

            before_status = subscription.status

            if event == _STATUS_CHANGING_EVENT:
                cycle = (checkout.get("subscription") or {}).get("cycle")
                tier = get_plan_tier(cycle) if cycle else None
                if tier is not None:
                    subscription.billing_cycle = tier.cycle
                    subscription.current_period_ends_at = add_months(
                        datetime.now(UTC), tier.months
                    )
                await repository.update_status(subscription, SubscriptionStatus.ACTIVE)

            await repository.add_audit_log(
                tenant_id=tenant_id,
                action=f"ASAAS_{event}",
                resource="subscriptions",
                before={"status": before_status},
                after={"status": subscription.status, "checkout_id": checkout.get("id")},
            )
            await repository.commit()
