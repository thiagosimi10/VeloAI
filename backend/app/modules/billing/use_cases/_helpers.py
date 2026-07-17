"""Helpers compartilhados entre os Use Cases de Billing — mesmo padrão de
`dashboard/use_cases/_helpers.py` e `knowledge/use_cases/_helpers.py`."""

from __future__ import annotations

from datetime import UTC, datetime

from veloai_shared.schema.master import Plan, Subscription, SubscriptionStatus

from app.modules.billing.schemas.billing import SubscriptionResponse


def to_subscription_response(subscription: Subscription, plan: Plan) -> SubscriptionResponse:
    days_remaining: int | None = None
    if (
        subscription.status == SubscriptionStatus.TRIAL.value
        and subscription.trial_ends_at is not None
    ):
        days_remaining = max(0, (subscription.trial_ends_at - datetime.now(UTC)).days)

    return SubscriptionResponse(
        plan_name=plan.name,
        plan_price=plan.price,
        status=subscription.status,
        trial_ends_at=subscription.trial_ends_at,
        current_period_ends_at=subscription.current_period_ends_at,
        days_remaining=days_remaining,
    )
