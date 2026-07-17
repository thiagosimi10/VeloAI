"""Tool MCP: cadastra um cliente, conforme docs/20-MCP-TOOLS.md (`CreateCustomer`,
"Exemplo Completo": "Cadastre um cliente chamado João Silva."). Reaproveita
`CreateCustomerUseCase`/`CreateCustomerRequest` já existentes — os campos de endereço
(não expostos aqui) usam o default do schema."""

from __future__ import annotations

import uuid
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.core.ai_tools import AITool
from app.core.database import TenantConnectionManager
from app.modules.customers.permissions import CUSTOMERS_CREATE
from app.modules.customers.schemas.customer import CreateCustomerRequest
from app.modules.customers.use_cases.create_customer_use_case import CreateCustomerUseCase


class CreateCustomerToolInput(BaseModel):
    type: Literal["PF", "PJ"]
    name: str = Field(min_length=3, max_length=200)
    document: str = Field(min_length=11, max_length=18)
    email: str | None = None
    phone: str | None = None


class CreateCustomerTool(AITool):
    name = "CreateCustomer"
    description = "Cadastra um novo cliente (pessoa física ou jurídica)."
    permission = CUSTOMERS_CREATE
    service = "customers"
    input_model = CreateCustomerToolInput

    async def execute(
        self,
        *,
        connection_manager: TenantConnectionManager,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        tool_input = CreateCustomerToolInput.model_validate(arguments)
        payload = CreateCustomerRequest(
            type=tool_input.type,
            name=tool_input.name,
            document=tool_input.document,
            email=tool_input.email,
            phone=tool_input.phone,
        )
        use_case = CreateCustomerUseCase(connection_manager=connection_manager)
        response = await use_case.execute(
            tenant_id=tenant_id,
            database_name=database_name,
            actor_user_id=actor_user_id,
            payload=payload,
        )
        return response.model_dump(mode="json")
