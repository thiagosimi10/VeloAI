import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from veloai_shared.exceptions import ConflictError, NotFoundError
from veloai_shared.schema.master import Plan, Subscription, SubscriptionStatus

from app.modules.billing.use_cases.cancel_subscription_use_case import (
    CancelSubscriptionUseCase,
)
from app.modules.billing.use_cases.get_subscription_use_case import GetSubscriptionUseCase


def _master_session(session: AsyncMock):
    @asynccontextmanager
    async def _session_context(*_args: object, **_kwargs: object):
        yield session

    return _session_context


def _plan() -> Plan:
    return Plan(id=uuid.uuid4(), name="VeloAI Professional", price=Decimal("129.90"), active=True)


async def test_get_subscription_returns_trial_with_days_remaining() -> None:
    tenant_id = uuid.uuid4()
    plan = _plan()
    subscription = Subscription(
        tenant_id=tenant_id,
        plan_id=plan.id,
        status=SubscriptionStatus.TRIAL.value,
        trial_ends_at=datetime.now(UTC) + timedelta(days=5),
    )

    with (
        patch(
            "app.modules.billing.use_cases.get_subscription_use_case.get_master_session",
            _master_session(AsyncMock()),
        ),
        patch(
            "app.modules.billing.use_cases.get_subscription_use_case.SubscriptionRepository"
        ) as repo_cls,
    ):
        repo_cls.return_value.get_by_tenant_id = AsyncMock(return_value=subscription)
        repo_cls.return_value.get_plan = AsyncMock(return_value=plan)

        result = await GetSubscriptionUseCase().execute(tenant_id=tenant_id)

    assert result.plan_name == "VeloAI Professional"
    assert result.status == SubscriptionStatus.TRIAL.value
    # `timedelta.days` trunca para baixo — um pouquinho menos que 5 dias vira 4.
    assert result.days_remaining == 4


async def test_get_subscription_raises_not_found_when_missing() -> None:
    with (
        patch(
            "app.modules.billing.use_cases.get_subscription_use_case.get_master_session",
            _master_session(AsyncMock()),
        ),
        patch(
            "app.modules.billing.use_cases.get_subscription_use_case.SubscriptionRepository"
        ) as repo_cls,
    ):
        repo_cls.return_value.get_by_tenant_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await GetSubscriptionUseCase().execute(tenant_id=uuid.uuid4())


async def test_cancel_subscription_transitions_to_canceled() -> None:
    tenant_id = uuid.uuid4()
    plan = _plan()
    subscription = Subscription(
        tenant_id=tenant_id, plan_id=plan.id, status=SubscriptionStatus.ACTIVE.value
    )

    with (
        patch(
            "app.modules.billing.use_cases.cancel_subscription_use_case.get_master_session",
            _master_session(AsyncMock()),
        ),
        patch(
            "app.modules.billing.use_cases.cancel_subscription_use_case.SubscriptionRepository"
        ) as repo_cls,
    ):
        repo = repo_cls.return_value
        repo.get_by_tenant_id = AsyncMock(return_value=subscription)
        repo.get_plan = AsyncMock(return_value=plan)

        async def _update_status(sub: Subscription, status: SubscriptionStatus) -> Subscription:
            sub.status = status.value
            return sub

        repo.update_status = AsyncMock(side_effect=_update_status)
        repo.add_audit_log = AsyncMock()
        repo.commit = AsyncMock()

        result = await CancelSubscriptionUseCase().execute(tenant_id=tenant_id)

    assert result.status == SubscriptionStatus.CANCELED.value
    repo.add_audit_log.assert_awaited_once()
    assert repo.add_audit_log.call_args.kwargs["action"] == "SUBSCRIPTION_CANCELED"


async def test_cancel_subscription_raises_conflict_when_already_canceled() -> None:
    tenant_id = uuid.uuid4()
    subscription = Subscription(
        tenant_id=tenant_id, plan_id=uuid.uuid4(), status=SubscriptionStatus.CANCELED.value
    )

    with (
        patch(
            "app.modules.billing.use_cases.cancel_subscription_use_case.get_master_session",
            _master_session(AsyncMock()),
        ),
        patch(
            "app.modules.billing.use_cases.cancel_subscription_use_case.SubscriptionRepository"
        ) as repo_cls,
    ):
        repo_cls.return_value.get_by_tenant_id = AsyncMock(return_value=subscription)

        with pytest.raises(ConflictError):
            await CancelSubscriptionUseCase().execute(tenant_id=tenant_id)
