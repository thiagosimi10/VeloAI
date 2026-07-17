"""Tool MCP: retorna a série histórica de faturamento dos últimos meses, conforme
docs/15-RELATORIOS-INTELIGENTES.md ("perguntas em linguagem natural sobre o negócio").
Reaproveita `GetRevenueTimeseriesUseCase` já existente — nenhuma query nova."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel

from app.core.ai_tools import AITool
from app.core.database import TenantConnectionManager
from app.modules.dashboard.permissions import DASHBOARD_VIEW
from app.modules.dashboard.use_cases.get_revenue_timeseries_use_case import (
    GetRevenueTimeseriesUseCase,
)


class GetRevenueTimeseriesToolInput(BaseModel):
    pass


class GetRevenueTimeseriesTool(AITool):
    name = "GetRevenueTimeseries"
    description = "Retorna o faturamento mensal dos últimos 6 meses, mês a mês."
    permission = DASHBOARD_VIEW
    service = "dashboard"
    input_model = GetRevenueTimeseriesToolInput

    async def execute(
        self,
        *,
        connection_manager: TenantConnectionManager,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        GetRevenueTimeseriesToolInput.model_validate(arguments)
        use_case = GetRevenueTimeseriesUseCase(connection_manager=connection_manager)
        points = await use_case.execute(tenant_id=tenant_id, database_name=database_name)
        return {"points": [point.model_dump(mode="json") for point in points]}
