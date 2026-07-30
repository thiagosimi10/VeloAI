"""Caso de uso: série histórica de receita dos últimos 30 dias (dia corrente incluso),
para o gráfico de Receita Diária do Dashboard."""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from decimal import Decimal

from app.core.database import TenantConnectionManager
from app.modules.dashboard.repositories.dashboard_repository import DashboardRepository
from app.modules.dashboard.schemas.dashboard import RevenueTimeSeriesPoint

_DAYS_BACK = 30


class GetDailyRevenueTimeseriesUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str
    ) -> list[RevenueTimeSeriesPoint]:
        today = date.today()
        start = today - timedelta(days=_DAYS_BACK - 1)
        end = today + timedelta(days=1)

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = DashboardRepository(session)
            totals_by_day = await repository.sum_revenue_by_day(start, end)

        return [
            RevenueTimeSeriesPoint(
                period=(start + timedelta(days=offset)).strftime("%Y-%m-%d"),
                revenue=totals_by_day.get(start + timedelta(days=offset), Decimal("0.00")),
            )
            for offset in range(_DAYS_BACK)
        ]
