"""Caso de uso: montar o resumo de indicadores do Dashboard, agregando dados de
Clientes, Produtos, Serviços, Ordens de Serviço, Vendas e Financeiro — sem tabela
própria (ver `app/modules/README.md`)."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from app.core.database import TenantConnectionManager
from app.modules.dashboard.repositories.dashboard_repository import DashboardRepository
from app.modules.dashboard.schemas.dashboard import DashboardSummaryResponse
from app.modules.dashboard.use_cases._helpers import add_months, first_day_of_month


class GetDashboardSummaryUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str
    ) -> DashboardSummaryResponse:
        today = date.today()
        this_month_start = first_day_of_month(today)
        next_month_start = add_months(this_month_start, 1)
        last_month_start = add_months(this_month_start, -1)

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = DashboardRepository(session)

            total_customers = await repository.count_customers()
            total_products = await repository.count_products()
            total_services = await repository.count_services()
            orders_by_status = await repository.count_orders_by_status()
            sales_by_status = await repository.count_sales_by_status()

            revenue_this_month, sales_count_this_month = await repository.sum_revenue_between(
                this_month_start, next_month_start
            )
            revenue_last_month, _ = await repository.sum_revenue_between(
                last_month_start, this_month_start
            )

            revenue_change_percentage: Decimal | None
            if revenue_last_month > 0:
                revenue_change_percentage = round(
                    (revenue_this_month - revenue_last_month) / revenue_last_month * 100, 2
                )
            else:
                revenue_change_percentage = None

            average_ticket = (
                round(revenue_this_month / sales_count_this_month, 2)
                if sales_count_this_month > 0
                else Decimal("0.00")
            )

            accounts_receivable_pending_total = (
                await repository.sum_accounts_receivable_pending()
            )
            accounts_receivable_overdue_count = (
                await repository.count_accounts_receivable_overdue()
            )
            accounts_payable_pending_total = await repository.sum_accounts_payable_pending()
            accounts_payable_overdue_count = await repository.count_accounts_payable_overdue()
            cash_balance = await repository.sum_cash_balance()
            critical_stock_count = await repository.count_critical_stock()

        return DashboardSummaryResponse(
            total_customers=total_customers,
            total_products=total_products,
            total_services=total_services,
            orders_by_status=orders_by_status,
            sales_by_status=sales_by_status,
            revenue_this_month=revenue_this_month,
            revenue_last_month=revenue_last_month,
            revenue_change_percentage=revenue_change_percentage,
            average_ticket=average_ticket,
            accounts_receivable_pending_total=accounts_receivable_pending_total,
            accounts_receivable_overdue_count=accounts_receivable_overdue_count,
            accounts_payable_pending_total=accounts_payable_pending_total,
            accounts_payable_overdue_count=accounts_payable_overdue_count,
            cash_balance=cash_balance,
            critical_stock_count=critical_stock_count,
        )
