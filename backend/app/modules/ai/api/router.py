"""Controller do módulo de IA. Responsabilidade: receber requisição, validar permissão
via `require_permission` e delegar ao Use Case — nunca conter regra de negócio
(00-AI-CONSTITUTION.md)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from veloai_shared.responses import SuccessResponse

from app.core.ai_gateway_client import AIGatewayClient, get_ai_gateway_client
from app.core.database import TenantConnectionManager, get_tenant_connection_manager
from app.core.dependencies import CurrentUser, require_permission
from app.modules.ai.permissions import AI_USE
from app.modules.ai.schemas.ai import (
    AiConversationFilterParams,
    AiConversationResponse,
    AskAIRequest,
    AskAIResponse,
)
from app.modules.ai.use_cases.ask_ai_use_case import AskAIUseCase
from app.modules.ai.use_cases.list_ai_conversations_use_case import ListAiConversationsUseCase

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/ask")
async def ask_ai(
    payload: AskAIRequest,
    current_user: CurrentUser = Depends(require_permission(AI_USE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
    ai_gateway_client: AIGatewayClient = Depends(get_ai_gateway_client),
) -> SuccessResponse[AskAIResponse]:
    use_case = AskAIUseCase(
        connection_manager=connection_manager, ai_gateway_client=ai_gateway_client
    )
    response = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        role=current_user.role,
        prompt=payload.prompt,
    )
    return SuccessResponse(message="Resposta gerada com sucesso.", data=response)


@router.get("/conversations")
async def list_ai_conversations(
    filters: AiConversationFilterParams = Depends(),
    current_user: CurrentUser = Depends(require_permission(AI_USE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[AiConversationResponse]]:
    use_case = ListAiConversationsUseCase(connection_manager=connection_manager)
    result = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        filters=filters,
    )
    return SuccessResponse(
        message="Histórico de uso de IA listado com sucesso.", data=result.items, meta=result.meta
    )
