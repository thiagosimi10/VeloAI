"""Tool MCP: busca um cliente pelo id, conforme docs/20-MCP-TOOLS.md (`GetCustomer`).
Reaproveita `GetCustomerUseCase` já existente."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel

from app.core.ai_tools import AITool
from app.core.database import TenantConnectionManager
from app.modules.customers.permissions import CUSTOMERS_VIEW
from app.modules.customers.use_cases.get_customer_use_case import GetCustomerUseCase


class GetCustomerToolInput(BaseModel):
    customer_id: str


class GetCustomerTool(AITool):
    name = "GetCustomer"
    description = "Busca os detalhes de um cliente pelo seu ID."
    permission = CUSTOMERS_VIEW
    service = "customers"
    input_model = GetCustomerToolInput

    async def execute(
        self,
        *,
        connection_manager: TenantConnectionManager,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        tool_input = GetCustomerToolInput.model_validate(arguments)
        customer_id = uuid.UUID(tool_input.customer_id)
        use_case = GetCustomerUseCase(connection_manager=connection_manager)
        response = await use_case.execute(
            tenant_id=tenant_id, database_name=database_name, customer_id=customer_id
        )
        return response.model_dump(mode="json")
