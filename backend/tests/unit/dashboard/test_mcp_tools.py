import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from app.modules.dashboard.mcp_tools.get_dashboard_summary_tool import GetDashboardSummaryTool
from app.modules.dashboard.mcp_tools.get_revenue_timeseries_tool import (
    GetRevenueTimeseriesTool,
)
from app.modules.dashboard.mcp_tools.get_top_selling_products_tool import (
    GetTopSellingProductsTool,
)
from app.modules.dashboard.permissions import DASHBOARD_VIEW
from app.modules.dashboard.schemas.dashboard import (
    DashboardSummaryResponse,
    RevenueTimeSeriesPoint,
    TopProductItem,
)


def _build_summary() -> DashboardSummaryResponse:
    return DashboardSummaryResponse(
        total_customers=10,
        total_products=20,
        total_services=5,
        orders_by_status={"open": 3, "closed": 7},
        revenue_this_month=1000,
        revenue_last_month=800,
        revenue_change_percentage=25,
        average_ticket=100,
        accounts_receivable_pending_total=500,
        accounts_receivable_overdue_count=1,
        accounts_payable_pending_total=300,
        accounts_payable_overdue_count=0,
        cash_balance=2000,
        critical_stock_count=2,
    )


def test_get_dashboard_summary_tool_has_correct_permission_and_service() -> None:
    tool = GetDashboardSummaryTool()

    assert tool.permission == DASHBOARD_VIEW
    assert tool.service == "dashboard"
    assert tool.parameters_schema()["properties"] == {}


async def test_get_dashboard_summary_tool_executes_use_case() -> None:
    connection_manager = MagicMock()
    tool = GetDashboardSummaryTool()
    summary = _build_summary()

    with patch(
        "app.modules.dashboard.mcp_tools.get_dashboard_summary_tool.GetDashboardSummaryUseCase"
    ) as use_case_cls:
        use_case_cls.return_value.execute = AsyncMock(return_value=summary)

        result = await tool.execute(
            connection_manager=connection_manager,
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            arguments={},
        )

    assert result["total_customers"] == 10
    assert result["revenue_change_percentage"] == "25"
    use_case_cls.return_value.execute.assert_awaited_once()


def test_get_revenue_timeseries_tool_has_correct_permission_and_service() -> None:
    tool = GetRevenueTimeseriesTool()

    assert tool.permission == DASHBOARD_VIEW
    assert tool.service == "dashboard"
    assert tool.parameters_schema()["properties"] == {}


async def test_get_revenue_timeseries_tool_executes_use_case() -> None:
    connection_manager = MagicMock()
    tool = GetRevenueTimeseriesTool()
    points = [RevenueTimeSeriesPoint(period="2026-01", revenue=1000)]

    with patch(
        "app.modules.dashboard.mcp_tools.get_revenue_timeseries_tool.GetRevenueTimeseriesUseCase"
    ) as use_case_cls:
        use_case_cls.return_value.execute = AsyncMock(return_value=points)

        result = await tool.execute(
            connection_manager=connection_manager,
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            arguments={},
        )

    assert result["points"] == [{"period": "2026-01", "revenue": "1000"}]
    use_case_cls.return_value.execute.assert_awaited_once()


def test_get_top_selling_products_tool_has_correct_permission_and_service() -> None:
    tool = GetTopSellingProductsTool()

    assert tool.permission == DASHBOARD_VIEW
    assert tool.service == "dashboard"
    assert tool.parameters_schema()["properties"]["limit"]["default"] == 5


async def test_get_top_selling_products_tool_executes_use_case_with_default_limit() -> None:
    connection_manager = MagicMock()
    tool = GetTopSellingProductsTool()
    product_id = uuid.uuid4()
    items = [TopProductItem(product_id=product_id, name="Produto A", quantity_sold=42)]

    with patch(
        "app.modules.dashboard.mcp_tools.get_top_selling_products_tool.GetTopProductsUseCase"
    ) as use_case_cls:
        use_case_cls.return_value.execute = AsyncMock(return_value=items)

        result = await tool.execute(
            connection_manager=connection_manager,
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            arguments={},
        )

    assert result["items"] == [
        {"product_id": str(product_id), "name": "Produto A", "quantity_sold": 42}
    ]
    assert use_case_cls.return_value.execute.call_args.kwargs["limit"] == 5


async def test_get_top_selling_products_tool_executes_use_case_with_custom_limit() -> None:
    connection_manager = MagicMock()
    tool = GetTopSellingProductsTool()

    with patch(
        "app.modules.dashboard.mcp_tools.get_top_selling_products_tool.GetTopProductsUseCase"
    ) as use_case_cls:
        use_case_cls.return_value.execute = AsyncMock(return_value=[])

        await tool.execute(
            connection_manager=connection_manager,
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            arguments={"limit": 10},
        )

    assert use_case_cls.return_value.execute.call_args.kwargs["limit"] == 10
