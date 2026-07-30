"""Caso de uso: série histórica de novos clientes cadastrados nos últimos 6 meses (mês
corrente incluso), para o gráfico de Novos Clientes do Dashboard."""

from __future__ import annotations

import uuid
from datetime import date

from app.core.database import TenantConnectionManager
from app.modules.dashboard.repositories.dashboard_repository import DashboardRepository
from app.modules.dashboard.schemas.dashboard import NewCustomersTimeSeriesPoint
from app.modules.dashboard.use_cases._helpers import add_months, first_day_of_month

_MONTHS_BACK = 6


class GetNewCustomersTimeseriesUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str
    ) -> list[NewCustomersTimeSeriesPoint]:
        current_month_start = first_day_of_month(date.today())
        month_starts = [
            add_months(current_month_start, -offset) for offset in range(_MONTHS_BACK - 1, -1, -1)
        ]

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = DashboardRepository(session)

            points: list[NewCustomersTimeSeriesPoint] = []
            for month_start in month_starts:
                month_end = add_months(month_start, 1)
                count = await repository.count_customers_between(month_start, month_end)
                points.append(
                    NewCustomersTimeSeriesPoint(period=month_start.strftime("%Y-%m"), count=count)
                )

        return points
