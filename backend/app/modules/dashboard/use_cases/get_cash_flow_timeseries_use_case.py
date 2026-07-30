"""Caso de uso: série histórica de entradas x saídas de caixa dos últimos 30 dias (dia
corrente incluso), para o gráfico de Fluxo de Caixa do Dashboard."""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from decimal import Decimal

from app.core.database import TenantConnectionManager
from app.modules.dashboard.repositories.dashboard_repository import DashboardRepository
from app.modules.dashboard.schemas.dashboard import CashFlowTimeSeriesPoint

_DAYS_BACK = 30


class GetCashFlowTimeseriesUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str
    ) -> list[CashFlowTimeSeriesPoint]:
        today = date.today()
        start = today - timedelta(days=_DAYS_BACK - 1)
        end = today + timedelta(days=1)

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = DashboardRepository(session)
            totals_by_day = await repository.sum_cash_flow_by_day(start, end)

        points: list[CashFlowTimeSeriesPoint] = []
        for offset in range(_DAYS_BACK):
            day = start + timedelta(days=offset)
            day_totals = totals_by_day.get(day, {"in": Decimal("0.00"), "out": Decimal("0.00")})
            points.append(
                CashFlowTimeSeriesPoint(
                    period=day.strftime("%Y-%m-%d"),
                    cash_in=day_totals.get("in", Decimal("0.00")),
                    cash_out=day_totals.get("out", Decimal("0.00")),
                )
            )

        return points
