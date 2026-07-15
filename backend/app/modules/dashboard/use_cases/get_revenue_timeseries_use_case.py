"""Caso de uso: série histórica de receita dos últimos 6 meses (mês corrente incluso),
para o gráfico de linha do Dashboard."""

from __future__ import annotations

import uuid
from datetime import date

from app.core.database import TenantConnectionManager
from app.modules.dashboard.repositories.dashboard_repository import DashboardRepository
from app.modules.dashboard.schemas.dashboard import RevenueTimeSeriesPoint
from app.modules.dashboard.use_cases._helpers import add_months, first_day_of_month

_MONTHS_BACK = 6


class GetRevenueTimeseriesUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str
    ) -> list[RevenueTimeSeriesPoint]:
        current_month_start = first_day_of_month(date.today())
        month_starts = [
            add_months(current_month_start, -offset) for offset in range(_MONTHS_BACK - 1, -1, -1)
        ]

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = DashboardRepository(session)

            points: list[RevenueTimeSeriesPoint] = []
            for month_start in month_starts:
                month_end = add_months(month_start, 1)
                revenue, _ = await repository.sum_revenue_between(month_start, month_end)
                points.append(
                    RevenueTimeSeriesPoint(period=month_start.strftime("%Y-%m"), revenue=revenue)
                )

        return points
