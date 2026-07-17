import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from veloai_shared.exceptions import SubscriptionInactiveError
from veloai_shared.schema.master import Subscription, SubscriptionStatus

from app.modules.billing.services.subscription_gate_service import (
    ensure_subscription_active,
    resolve_subscription_status,
)


async def test_resolve_subscription_status_expires_trial_past_due() -> None:
    subscription = Subscription(
        tenant_id=uuid.uuid4(),
        plan_id=uuid.uuid4(),
        status=SubscriptionStatus.TRIAL.value,
        trial_ends_at=datetime.now(UTC) - timedelta(days=1),
    )
    repository = MagicMock()

    async def _update_status(sub: Subscription, status: SubscriptionStatus) -> Subscription:
        sub.status = status.value
        return sub

    repository.update_status = AsyncMock(side_effect=_update_status)
    repository.commit = AsyncMock()

    status_value = await resolve_subscription_status(repository, subscription)

    assert status_value == SubscriptionStatus.EXPIRED.value
    repository.commit.assert_awaited_once()


async def test_resolve_subscription_status_keeps_trial_within_period() -> None:
    subscription = Subscription(
        tenant_id=uuid.uuid4(),
        plan_id=uuid.uuid4(),
        status=SubscriptionStatus.TRIAL.value,
        trial_ends_at=datetime.now(UTC) + timedelta(days=1),
    )
    repository = MagicMock()
    repository.update_status = AsyncMock()
    repository.commit = AsyncMock()

    status_value = await resolve_subscription_status(repository, subscription)

    assert status_value == SubscriptionStatus.TRIAL.value
    repository.update_status.assert_not_awaited()


async def test_ensure_subscription_active_raises_for_canceled() -> None:
    tenant_id = uuid.uuid4()
    subscription = Subscription(
        tenant_id=tenant_id, plan_id=uuid.uuid4(), status=SubscriptionStatus.CANCELED.value
    )

    with patch(
        "app.modules.billing.services.subscription_gate_service.SubscriptionRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_tenant_id = AsyncMock(return_value=subscription)

        with pytest.raises(SubscriptionInactiveError):
            await ensure_subscription_active(AsyncMock(), tenant_id)


async def test_ensure_subscription_active_passes_for_active() -> None:
    tenant_id = uuid.uuid4()
    subscription = Subscription(
        tenant_id=tenant_id, plan_id=uuid.uuid4(), status=SubscriptionStatus.ACTIVE.value
    )

    with patch(
        "app.modules.billing.services.subscription_gate_service.SubscriptionRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_tenant_id = AsyncMock(return_value=subscription)

        await ensure_subscription_active(AsyncMock(), tenant_id)


async def test_ensure_subscription_active_passes_when_no_subscription_found() -> None:
    with patch(
        "app.modules.billing.services.subscription_gate_service.SubscriptionRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_tenant_id = AsyncMock(return_value=None)

        await ensure_subscription_active(AsyncMock(), uuid.uuid4())
