import uuid
from contextlib import asynccontextmanager
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from app.modules.dashboard.use_cases.get_dashboard_summary_use_case import (
    GetDashboardSummaryUseCase,
)
from app.modules.dashboard.use_cases.get_revenue_timeseries_use_case import (
    GetRevenueTimeseriesUseCase,
)
from app.modules.dashboard.use_cases.get_top_products_use_case import GetTopProductsUseCase


def _connection_manager_with_session(session: AsyncMock) -> MagicMock:
    @asynccontextmanager
    async def _session_context(*_args: object, **_kwargs: object):
        yield session

    manager = MagicMock()
    manager.session_for_tenant = MagicMock(side_effect=_session_context)
    return manager


async def test_get_dashboard_summary_computes_revenue_change_percentage() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = GetDashboardSummaryUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.dashboard.use_cases.get_dashboard_summary_use_case.DashboardRepository"
    ) as repo_cls:
        repo = repo_cls.return_value
        repo.count_customers = AsyncMock(return_value=10)
        repo.count_products = AsyncMock(return_value=20)
        repo.count_services = AsyncMock(return_value=5)
        repo.count_orders_by_status = AsyncMock(return_value={"open": 2, "completed": 8})
        repo.sum_revenue_between = AsyncMock(
            side_effect=[
                (Decimal("1100.00"), 4),  # mês corrente
                (Decimal("1000.00"), 3),  # mês anterior
            ]
        )
        repo.sum_accounts_receivable_pending = AsyncMock(return_value=Decimal("500.00"))
        repo.count_accounts_receivable_overdue = AsyncMock(return_value=1)
        repo.sum_accounts_payable_pending = AsyncMock(return_value=Decimal("200.00"))
        repo.count_accounts_payable_overdue = AsyncMock(return_value=0)
        repo.sum_cash_balance = AsyncMock(return_value=Decimal("3000.00"))
        repo.count_critical_stock = AsyncMock(return_value=2)

        result = await use_case.execute(tenant_id=uuid.uuid4(), database_name="tenant_abc")

    assert result.total_customers == 10
    assert result.orders_by_status == {"open": 2, "completed": 8}
    assert result.revenue_change_percentage == Decimal("10.00")
    assert result.average_ticket == Decimal("275.00")
    assert result.accounts_receivable_overdue_count == 1
    assert result.critical_stock_count == 2


async def test_get_dashboard_summary_avoids_division_by_zero_when_no_previous_revenue() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = GetDashboardSummaryUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.dashboard.use_cases.get_dashboard_summary_use_case.DashboardRepository"
    ) as repo_cls:
        repo = repo_cls.return_value
        repo.count_customers = AsyncMock(return_value=0)
        repo.count_products = AsyncMock(return_value=0)
        repo.count_services = AsyncMock(return_value=0)
        repo.count_orders_by_status = AsyncMock(return_value={})
        repo.sum_revenue_between = AsyncMock(
            side_effect=[
                (Decimal("0.00"), 0),  # mês corrente
                (Decimal("0.00"), 0),  # mês anterior
            ]
        )
        repo.sum_accounts_receivable_pending = AsyncMock(return_value=Decimal("0.00"))
        repo.count_accounts_receivable_overdue = AsyncMock(return_value=0)
        repo.sum_accounts_payable_pending = AsyncMock(return_value=Decimal("0.00"))
        repo.count_accounts_payable_overdue = AsyncMock(return_value=0)
        repo.sum_cash_balance = AsyncMock(return_value=Decimal("0.00"))
        repo.count_critical_stock = AsyncMock(return_value=0)

        result = await use_case.execute(tenant_id=uuid.uuid4(), database_name="tenant_abc")

    assert result.revenue_change_percentage is None
    assert result.average_ticket == Decimal("0.00")


async def test_get_revenue_timeseries_returns_six_months_including_current() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = GetRevenueTimeseriesUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.dashboard.use_cases.get_revenue_timeseries_use_case.DashboardRepository"
    ) as repo_cls:
        repo_cls.return_value.sum_revenue_between = AsyncMock(return_value=(Decimal("100.00"), 1))

        result = await use_case.execute(tenant_id=uuid.uuid4(), database_name="tenant_abc")

    assert len(result) == 6
    assert repo_cls.return_value.sum_revenue_between.await_count == 6
    periods = [point.period for point in result]
    assert periods == sorted(periods)
    assert len(set(periods)) == 6


async def test_get_top_products_maps_repository_rows() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = GetTopProductsUseCase(connection_manager=connection_manager)
    product_id = uuid.uuid4()

    with patch(
        "app.modules.dashboard.use_cases.get_top_products_use_case.DashboardRepository"
    ) as repo_cls:
        repo_cls.return_value.top_products_by_quantity = AsyncMock(
            return_value=[(product_id, "SSD Kingston 1TB", 15)]
        )

        result = await use_case.execute(
            tenant_id=uuid.uuid4(), database_name="tenant_abc", limit=5
        )

    assert len(result) == 1
    assert result[0].product_id == product_id
    assert result[0].name == "SSD Kingston 1TB"
    assert result[0].quantity_sold == 15
