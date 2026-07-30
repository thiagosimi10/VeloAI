"""Controller do módulo Dashboard. Responsabilidade: receber requisição, validar
permissão via `require_permission` e delegar ao Use Case — nunca conter regra de
negócio (00-AI-CONSTITUTION.md). Somente leitura — nenhum endpoint de escrita."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from veloai_shared.responses import SuccessResponse

from app.core.database import TenantConnectionManager, get_tenant_connection_manager
from app.core.dependencies import CurrentUser, require_permission
from app.modules.dashboard.permissions import DASHBOARD_VIEW
from app.modules.dashboard.schemas.dashboard import (
    CashFlowTimeSeriesPoint,
    CategoryProductCount,
    DashboardSummaryResponse,
    NewCustomersTimeSeriesPoint,
    RevenueTimeSeriesPoint,
    TopProductItem,
)
from app.modules.dashboard.use_cases.get_cash_flow_timeseries_use_case import (
    GetCashFlowTimeseriesUseCase,
)
from app.modules.dashboard.use_cases.get_daily_revenue_timeseries_use_case import (
    GetDailyRevenueTimeseriesUseCase,
)
from app.modules.dashboard.use_cases.get_dashboard_summary_use_case import (
    GetDashboardSummaryUseCase,
)
from app.modules.dashboard.use_cases.get_new_customers_timeseries_use_case import (
    GetNewCustomersTimeseriesUseCase,
)
from app.modules.dashboard.use_cases.get_products_by_category_use_case import (
    GetProductsByCategoryUseCase,
)
from app.modules.dashboard.use_cases.get_revenue_timeseries_use_case import (
    GetRevenueTimeseriesUseCase,
)
from app.modules.dashboard.use_cases.get_top_products_use_case import GetTopProductsUseCase

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
async def get_dashboard_summary(
    current_user: CurrentUser = Depends(require_permission(DASHBOARD_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[DashboardSummaryResponse]:
    use_case = GetDashboardSummaryUseCase(connection_manager=connection_manager)
    summary = await use_case.execute(
        tenant_id=current_user.tenant_id, database_name=current_user.database_name
    )
    return SuccessResponse(message="Resumo do Dashboard obtido com sucesso.", data=summary)


@router.get("/revenue-timeseries")
async def get_revenue_timeseries(
    current_user: CurrentUser = Depends(require_permission(DASHBOARD_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[RevenueTimeSeriesPoint]]:
    use_case = GetRevenueTimeseriesUseCase(connection_manager=connection_manager)
    points = await use_case.execute(
        tenant_id=current_user.tenant_id, database_name=current_user.database_name
    )
    return SuccessResponse(message="Série histórica de receita obtida com sucesso.", data=points)


@router.get("/revenue-timeseries-daily")
async def get_daily_revenue_timeseries(
    current_user: CurrentUser = Depends(require_permission(DASHBOARD_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[RevenueTimeSeriesPoint]]:
    use_case = GetDailyRevenueTimeseriesUseCase(connection_manager=connection_manager)
    points = await use_case.execute(
        tenant_id=current_user.tenant_id, database_name=current_user.database_name
    )
    return SuccessResponse(
        message="Série diária de receita obtida com sucesso.", data=points
    )


@router.get("/new-customers-timeseries")
async def get_new_customers_timeseries(
    current_user: CurrentUser = Depends(require_permission(DASHBOARD_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[NewCustomersTimeSeriesPoint]]:
    use_case = GetNewCustomersTimeseriesUseCase(connection_manager=connection_manager)
    points = await use_case.execute(
        tenant_id=current_user.tenant_id, database_name=current_user.database_name
    )
    return SuccessResponse(
        message="Série histórica de novos clientes obtida com sucesso.", data=points
    )


@router.get("/cash-flow-timeseries")
async def get_cash_flow_timeseries(
    current_user: CurrentUser = Depends(require_permission(DASHBOARD_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[CashFlowTimeSeriesPoint]]:
    use_case = GetCashFlowTimeseriesUseCase(connection_manager=connection_manager)
    points = await use_case.execute(
        tenant_id=current_user.tenant_id, database_name=current_user.database_name
    )
    return SuccessResponse(
        message="Série histórica de fluxo de caixa obtida com sucesso.", data=points
    )


@router.get("/products-by-category")
async def get_products_by_category(
    current_user: CurrentUser = Depends(require_permission(DASHBOARD_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[CategoryProductCount]]:
    use_case = GetProductsByCategoryUseCase(connection_manager=connection_manager)
    items = await use_case.execute(
        tenant_id=current_user.tenant_id, database_name=current_user.database_name
    )
    return SuccessResponse(message="Produtos por categoria obtidos com sucesso.", data=items)


@router.get("/top-products")
async def get_top_products(
    limit: int = Query(default=5, ge=1, le=20),
    current_user: CurrentUser = Depends(require_permission(DASHBOARD_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[TopProductItem]]:
    use_case = GetTopProductsUseCase(connection_manager=connection_manager)
    items = await use_case.execute(
        tenant_id=current_user.tenant_id, database_name=current_user.database_name, limit=limit
    )
    return SuccessResponse(message="Produtos mais vendidos obtidos com sucesso.", data=items)
