"""Tool MCP: retorna o resumo executivo do Dashboard, conforme
docs/15-RELATORIOS-INTELIGENTES.md ("perguntas em linguagem natural sobre o negócio").
Reaproveita `GetDashboardSummaryUseCase` já existente — nenhuma query nova."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel

from app.core.ai_tools import AITool
from app.core.database import TenantConnectionManager
from app.modules.dashboard.permissions import DASHBOARD_VIEW
from app.modules.dashboard.use_cases.get_dashboard_summary_use_case import (
    GetDashboardSummaryUseCase,
)


class GetDashboardSummaryToolInput(BaseModel):
    pass


class GetDashboardSummaryTool(AITool):
    name = "GetDashboardSummary"
    description = (
        "Retorna o resumo executivo do negócio: faturamento do mês e variação, "
        "ticket médio, contas a receber e a pagar (pendentes e vencidas), saldo de "
        "caixa e itens em estoque crítico."
    )
    permission = DASHBOARD_VIEW
    service = "dashboard"
    input_model = GetDashboardSummaryToolInput

    async def execute(
        self,
        *,
        connection_manager: TenantConnectionManager,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        GetDashboardSummaryToolInput.model_validate(arguments)
        use_case = GetDashboardSummaryUseCase(connection_manager=connection_manager)
        summary = await use_case.execute(tenant_id=tenant_id, database_name=database_name)
        return summary.model_dump(mode="json")
