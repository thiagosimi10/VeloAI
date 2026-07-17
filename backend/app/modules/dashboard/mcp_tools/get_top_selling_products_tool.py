"""Tool MCP: retorna os produtos mais vendidos, conforme
docs/15-RELATORIOS-INTELIGENTES.md ("perguntas em linguagem natural sobre o negócio").
Reaproveita `GetTopProductsUseCase` já existente — nenhuma query nova."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field

from app.core.ai_tools import AITool
from app.core.database import TenantConnectionManager
from app.modules.dashboard.permissions import DASHBOARD_VIEW
from app.modules.dashboard.use_cases.get_top_products_use_case import GetTopProductsUseCase


class GetTopSellingProductsToolInput(BaseModel):
    limit: int = Field(default=5, ge=1, le=20)


class GetTopSellingProductsTool(AITool):
    name = "GetTopSellingProducts"
    description = "Retorna os produtos mais vendidos por quantidade, do maior para o menor."
    permission = DASHBOARD_VIEW
    service = "dashboard"
    input_model = GetTopSellingProductsToolInput

    async def execute(
        self,
        *,
        connection_manager: TenantConnectionManager,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        tool_input = GetTopSellingProductsToolInput.model_validate(arguments)
        use_case = GetTopProductsUseCase(connection_manager=connection_manager)
        items = await use_case.execute(
            tenant_id=tenant_id, database_name=database_name, limit=tool_input.limit
        )
        return {"items": [item.model_dump(mode="json") for item in items]}
