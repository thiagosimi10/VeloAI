import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from veloai_shared.exceptions import AuthenticationError, RateLimitedError
from veloai_shared.schema.master import AuditLog, Plan, PlatformAdmin, Subscription, Tenant
from veloai_shared.security import hash_password

from app.modules.admin.use_cases.change_platform_admin_password_use_case import (
    ChangePlatformAdminPasswordUseCase,
)
from app.modules.admin.use_cases.get_admin_summary_use_case import GetAdminSummaryUseCase
from app.modules.admin.use_cases.list_tenant_audit_log_use_case import (
    ListTenantAuditLogUseCase,
)
from app.modules.admin.use_cases.list_tenants_use_case import ListTenantsUseCase
from app.modules.admin.use_cases.login_platform_admin_use_case import (
    LoginPlatformAdminUseCase,
)
from app.modules.admin.use_cases.me_platform_admin_use_case import MePlatformAdminUseCase


def _master_session(session: AsyncMock):
    @asynccontextmanager
    async def _session_context(*_args: object, **_kwargs: object):
        yield session

    return _session_context


def _rate_limiter(*, blocked: bool = False) -> MagicMock:
    limiter = MagicMock()
    limiter.is_blocked = AsyncMock(return_value=blocked)
    limiter.register_failed_attempt = AsyncMock()
    limiter.reset = AsyncMock()
    return limiter


async def test_login_platform_admin_use_case_succeeds_with_correct_password() -> None:
    admin = PlatformAdmin(
        id=uuid.uuid4(),
        email="admin@veloai.internal",
        password_hash=hash_password("Sup3rSenha!"),
        first_name="Ana",
        last_name="Souza",
        active=True,
        force_password_change=True,
    )
    token_service = MagicMock()
    token_service.issue_token = MagicMock(return_value="fake-admin-token")
    rate_limiter = _rate_limiter()

    with (
        patch(
            "app.modules.admin.use_cases.login_platform_admin_use_case.get_master_session",
            _master_session(AsyncMock()),
        ),
        patch(
            "app.modules.admin.use_cases.login_platform_admin_use_case.AdminRepository"
        ) as repo_cls,
    ):
        repo_cls.return_value.get_platform_admin_by_email = AsyncMock(return_value=admin)

        result = await LoginPlatformAdminUseCase(
            token_service=token_service, rate_limiter=rate_limiter
        ).execute(email="admin@veloai.internal", password="Sup3rSenha!", ip="127.0.0.1")

    assert result.token == "fake-admin-token"
    assert result.admin_id == admin.id
    assert result.must_change_password is True
    rate_limiter.reset.assert_awaited_once()


async def test_login_platform_admin_use_case_fails_with_wrong_password() -> None:
    admin = PlatformAdmin(
        id=uuid.uuid4(),
        email="admin@veloai.internal",
        password_hash=hash_password("Sup3rSenha!"),
        first_name="Ana",
        active=True,
        force_password_change=False,
    )
    rate_limiter = _rate_limiter()

    with (
        patch(
            "app.modules.admin.use_cases.login_platform_admin_use_case.get_master_session",
            _master_session(AsyncMock()),
        ),
        patch(
            "app.modules.admin.use_cases.login_platform_admin_use_case.AdminRepository"
        ) as repo_cls,
    ):
        repo_cls.return_value.get_platform_admin_by_email = AsyncMock(return_value=admin)

        with pytest.raises(AuthenticationError):
            await LoginPlatformAdminUseCase(
                token_service=MagicMock(), rate_limiter=rate_limiter
            ).execute(email="admin@veloai.internal", password="wrong", ip="127.0.0.1")

    rate_limiter.register_failed_attempt.assert_awaited_once()


async def test_login_platform_admin_use_case_blocked_by_rate_limiter() -> None:
    rate_limiter = _rate_limiter(blocked=True)

    with pytest.raises(RateLimitedError):
        await LoginPlatformAdminUseCase(
            token_service=MagicMock(), rate_limiter=rate_limiter
        ).execute(email="admin@veloai.internal", password="whatever", ip="127.0.0.1")


async def test_change_platform_admin_password_use_case_updates_hash_and_flag() -> None:
    admin_id = uuid.uuid4()
    admin = PlatformAdmin(
        id=admin_id,
        email="admin@veloai.internal",
        password_hash=hash_password("SenhaAtual1!"),
        first_name="Ana",
        force_password_change=True,
    )

    with (
        patch(
            "app.modules.admin.use_cases.change_platform_admin_password_use_case."
            "get_master_session",
            _master_session(AsyncMock()),
        ),
        patch(
            "app.modules.admin.use_cases.change_platform_admin_password_use_case."
            "AdminRepository"
        ) as repo_cls,
    ):
        repo = repo_cls.return_value
        repo.get_platform_admin_by_id = AsyncMock(return_value=admin)
        repo.update_password = AsyncMock()
        repo.commit = AsyncMock()

        await ChangePlatformAdminPasswordUseCase().execute(
            admin_id=admin_id, current_password="SenhaAtual1!", new_password="NovaSenha1!"
        )

    repo.update_password.assert_awaited_once()
    assert repo.update_password.call_args.args[0] is admin


async def test_change_platform_admin_password_use_case_rejects_wrong_current_password() -> None:
    admin = PlatformAdmin(
        id=uuid.uuid4(),
        email="admin@veloai.internal",
        password_hash=hash_password("SenhaAtual1!"),
        first_name="Ana",
    )

    with (
        patch(
            "app.modules.admin.use_cases.change_platform_admin_password_use_case."
            "get_master_session",
            _master_session(AsyncMock()),
        ),
        patch(
            "app.modules.admin.use_cases.change_platform_admin_password_use_case."
            "AdminRepository"
        ) as repo_cls,
    ):
        repo_cls.return_value.get_platform_admin_by_id = AsyncMock(return_value=admin)

        with pytest.raises(AuthenticationError):
            await ChangePlatformAdminPasswordUseCase().execute(
                admin_id=admin.id, current_password="errada", new_password="NovaSenha1!"
            )


async def test_me_platform_admin_use_case_returns_profile() -> None:
    admin = PlatformAdmin(
        id=uuid.uuid4(),
        email="admin@veloai.internal",
        password_hash="hash",
        first_name="Ana",
        last_name="Souza",
        active=True,
        force_password_change=False,
    )

    with (
        patch(
            "app.modules.admin.use_cases.me_platform_admin_use_case.get_master_session",
            _master_session(AsyncMock()),
        ),
        patch(
            "app.modules.admin.use_cases.me_platform_admin_use_case.AdminRepository"
        ) as repo_cls,
    ):
        repo_cls.return_value.get_platform_admin_by_id = AsyncMock(return_value=admin)

        profile = await MePlatformAdminUseCase().execute(admin_id=admin.id)

    assert profile.email == "admin@veloai.internal"
    assert profile.must_change_password is False


async def test_list_tenants_use_case_maps_plan_and_subscription() -> None:
    plan = Plan(id=uuid.uuid4(), name="VeloAI Professional", price=Decimal("129.90"))
    tenant_id = uuid.uuid4()
    tenant = Tenant(
        id=tenant_id,
        legal_name="Assistência Silva",
        document="12345678000199",
        database_name="tenant_abc",
        database_host="postgres",
        database_port=5432,
        status="ACTIVE",
        plan_id=plan.id,
    )
    subscription = Subscription(
        tenant_id=tenant_id,
        plan_id=plan.id,
        status="TRIAL",
        trial_ends_at=datetime.now(UTC) + timedelta(days=3),
    )

    with (
        patch(
            "app.modules.admin.use_cases.list_tenants_use_case.get_master_session",
            _master_session(AsyncMock()),
        ),
        patch(
            "app.modules.admin.use_cases.list_tenants_use_case.AdminRepository"
        ) as repo_cls,
    ):
        repo = repo_cls.return_value
        repo.count_tenants = AsyncMock(return_value=1)
        repo.list_tenants = AsyncMock(return_value=[tenant])
        repo.get_plans_by_ids = AsyncMock(return_value={plan.id: plan})
        repo.get_subscriptions_by_tenant_ids = AsyncMock(
            return_value={tenant_id: subscription}
        )

        result = await ListTenantsUseCase().execute(page=1, page_size=20)

    assert len(result.items) == 1
    item = result.items[0]
    assert item.plan_name == "VeloAI Professional"
    assert item.subscription_status == "TRIAL"
    assert result.meta.total == 1


async def test_get_admin_summary_use_case_aggregates_counts() -> None:
    with (
        patch(
            "app.modules.admin.use_cases.get_admin_summary_use_case.get_master_session",
            _master_session(AsyncMock()),
        ),
        patch(
            "app.modules.admin.use_cases.get_admin_summary_use_case.AdminRepository"
        ) as repo_cls,
    ):
        repo = repo_cls.return_value
        repo.count_tenants = AsyncMock(return_value=3)
        repo.get_subscription_status_counts = AsyncMock(
            return_value={"TRIAL": 2, "ACTIVE": 1}
        )
        repo.get_estimated_mrr = AsyncMock(return_value=Decimal("129.90"))

        summary = await GetAdminSummaryUseCase().execute()

    assert summary.total_tenants == 3
    assert summary.trial_count == 2
    assert summary.active_count == 1
    assert summary.overdue_count == 0
    assert summary.estimated_mrr == Decimal("129.90")


async def test_list_tenant_audit_log_use_case_paginates() -> None:
    tenant_id = uuid.uuid4()
    entry = AuditLog(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        action="SUBSCRIPTION_CANCELED",
        resource="subscriptions",
        created_at=datetime.now(UTC),
    )

    with (
        patch(
            "app.modules.admin.use_cases.list_tenant_audit_log_use_case.get_master_session",
            _master_session(AsyncMock()),
        ),
        patch(
            "app.modules.admin.use_cases.list_tenant_audit_log_use_case.AdminRepository"
        ) as repo_cls,
    ):
        repo = repo_cls.return_value
        repo.count_audit_logs = AsyncMock(return_value=1)
        repo.list_audit_logs = AsyncMock(return_value=[entry])

        result = await ListTenantAuditLogUseCase().execute(
            tenant_id=tenant_id, page=1, page_size=20
        )

    assert len(result.items) == 1
    assert result.items[0].action == "SUBSCRIPTION_CANCELED"
    assert result.meta.total == 1
