"""Regra central do módulo Billing: se um tenant pode ou não usar o sistema, conforme
31-BILLING.md ("Nenhum Tenant poderá utilizar o sistema após suspensão definitiva").
Cross-cutting o suficiente para ser chamado tanto pelos Use Cases do próprio módulo
quanto por `app/core/dependencies.py::require_active_subscription` — mesmo padrão de
`require_permission` importando de `app.modules.auth`."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.exceptions import SubscriptionInactiveError
from veloai_shared.schema.master import Subscription, SubscriptionStatus

from app.modules.billing.repositories.subscription_repository import SubscriptionRepository

_INACTIVE_STATUSES = {
    SubscriptionStatus.EXPIRED.value,
    SubscriptionStatus.CANCELED.value,
    SubscriptionStatus.SUSPENDED.value,
}


async def resolve_subscription_status(
    repository: SubscriptionRepository, subscription: Subscription
) -> str:
    """Expira o Trial na hora certa, sem depender de um scheduler (que não existe
    ainda) — a primeira requisição feita após `trial_ends_at` já reflete o estado
    real."""

    if (
        subscription.status == SubscriptionStatus.TRIAL.value
        and subscription.trial_ends_at is not None
        and subscription.trial_ends_at < datetime.now(UTC)
    ):
        await repository.update_status(subscription, SubscriptionStatus.EXPIRED)
        await repository.commit()

    return subscription.status


async def ensure_subscription_active(session: AsyncSession, tenant_id: uuid.UUID) -> None:
    """Levanta `SubscriptionInactiveError` (403) quando a assinatura do tenant está
    expirada/cancelada/suspensa. Tenants sem nenhuma Assinatura (nunca deveria
    acontecer para um tenant provisionado de verdade desde a Fase 17) não são
    bloqueados — não há o que enforçar sem um registro."""

    repository = SubscriptionRepository(session)
    subscription = await repository.get_by_tenant_id(tenant_id)
    if subscription is None:
        return

    status_value = await resolve_subscription_status(repository, subscription)
    if status_value in _INACTIVE_STATUSES:
        raise SubscriptionInactiveError(
            "Assinatura inativa. Regularize sua assinatura para continuar usando o sistema."
        )
