"""Tool MCP: consulta o plano/status/vencimento da Assinatura do tenant, conforme
docs/31-BILLING.md ("IA poderá responder: Qual meu plano. Quando vence."). Reaproveita
`GetSubscriptionUseCase` já existente — nenhuma query nova. Somente leitura — cancelar
a própria assinatura via um prompt casual fica de fora desta fase, só pelo botão real
da UI."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel

from app.core.ai_tools import AITool
from app.core.database import TenantConnectionManager
from app.modules.billing.permissions import BILLING_VIEW
from app.modules.billing.use_cases.get_subscription_use_case import GetSubscriptionUseCase


class GetSubscriptionStatusToolInput(BaseModel):
    pass


class GetSubscriptionStatusTool(AITool):
    name = "GetSubscriptionStatus"
    description = (
        "Retorna o plano, valor, status e data de vencimento da assinatura da empresa."
    )
    permission = BILLING_VIEW
    service = "billing"
    input_model = GetSubscriptionStatusToolInput

    async def execute(
        self,
        *,
        connection_manager: TenantConnectionManager,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        GetSubscriptionStatusToolInput.model_validate(arguments)
        use_case = GetSubscriptionUseCase()
        subscription = await use_case.execute(tenant_id=tenant_id)
        return subscription.model_dump(mode="json")
