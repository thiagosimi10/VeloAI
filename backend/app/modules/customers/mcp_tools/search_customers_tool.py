"""Tool MCP: busca clientes cadastrados, conforme docs/20-MCP-TOOLS.md
(`SearchCustomers`). Reaproveita `ListCustomersUseCase` já existente — pagina fixa em
`page=1`/`page_size=10` (a IA não precisa controlar paginação)."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel

from app.core.ai_tools import AITool
from app.core.database import TenantConnectionManager
from app.modules.customers.permissions import CUSTOMERS_VIEW
from app.modules.customers.schemas.customer import CustomerFilterParams
from app.modules.customers.use_cases.list_customers_use_case import ListCustomersUseCase


class SearchCustomersToolInput(BaseModel):
    search: str | None = None


class SearchCustomersTool(AITool):
    name = "SearchCustomers"
    description = "Busca clientes cadastrados pelo nome, documento ou e-mail."
    permission = CUSTOMERS_VIEW
    service = "customers"
    input_model = SearchCustomersToolInput

    async def execute(
        self,
        *,
        connection_manager: TenantConnectionManager,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        tool_input = SearchCustomersToolInput.model_validate(arguments)
        use_case = ListCustomersUseCase(connection_manager=connection_manager)
        result = await use_case.execute(
            tenant_id=tenant_id,
            database_name=database_name,
            filters=CustomerFilterParams(search=tool_input.search, page=1, page_size=10),
        )
        return {
            "items": [item.model_dump(mode="json") for item in result.items],
            "total": result.meta.total,
        }
