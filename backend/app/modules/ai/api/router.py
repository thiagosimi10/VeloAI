"""Controller do módulo de IA. Responsabilidade: receber requisição, validar permissão
via `require_permission` e delegar ao Use Case — nunca conter regra de negócio
(00-AI-CONSTITUTION.md)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from veloai_shared.exceptions import ValidationError
from veloai_shared.responses import SuccessResponse

from app.core.ai_gateway_client import AIGatewayClient, get_ai_gateway_client
from app.core.ai_uploads import AiUploadStore, get_ai_upload_store
from app.core.database import TenantConnectionManager, get_tenant_connection_manager
from app.core.dependencies import CurrentUser, require_permission
from app.modules.ai.permissions import AI_USE
from app.modules.ai.schemas.ai import (
    AiConversationFilterParams,
    AiConversationResponse,
    AiUploadResponse,
    AskAIRequest,
    AskAIResponse,
)
from app.modules.ai.use_cases.ask_ai_use_case import AskAIUseCase
from app.modules.ai.use_cases.list_ai_conversations_use_case import ListAiConversationsUseCase

router = APIRouter(prefix="/ai", tags=["ai"])

_MAX_UPLOAD_FILE_SIZE_BYTES = 5 * 1024 * 1024


@router.post("/ask")
async def ask_ai(
    payload: AskAIRequest,
    current_user: CurrentUser = Depends(require_permission(AI_USE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
    ai_gateway_client: AIGatewayClient = Depends(get_ai_gateway_client),
    ai_upload_store: AiUploadStore = Depends(get_ai_upload_store),
) -> SuccessResponse[AskAIResponse]:
    use_case = AskAIUseCase(
        connection_manager=connection_manager,
        ai_gateway_client=ai_gateway_client,
        ai_upload_store=ai_upload_store,
    )
    response = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        role=current_user.role,
        prompt=payload.prompt,
        upload_id=payload.upload_id,
    )
    return SuccessResponse(message="Resposta gerada com sucesso.", data=response)


@router.post("/uploads", status_code=201)
async def upload_ai_file(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(require_permission(AI_USE)),
    ai_upload_store: AiUploadStore = Depends(get_ai_upload_store),
) -> SuccessResponse[AiUploadResponse]:
    """Anexa um arquivo (CSV/XLSX) à conversa antes de enviar a mensagem — o `upload_id`
    retornado aqui deve ser incluído em `AskAIRequest.upload_id` na próxima chamada a
    `/ai/ask`, para a IA saber que o arquivo existe e poder chamar a Tool
    `ImportProductsFromFile` com ele."""

    data = await file.read()
    if len(data) > _MAX_UPLOAD_FILE_SIZE_BYTES:
        raise ValidationError("Arquivo muito grande. O limite é 5MB.", code="UPLOAD_FILE_TOO_LARGE")

    filename = file.filename or "arquivo"
    upload_id = await ai_upload_store.save(
        tenant_id=str(current_user.tenant_id), filename=filename, data=data
    )
    preview = await ai_upload_store.preview(tenant_id=str(current_user.tenant_id), upload_id=upload_id)
    assert preview is not None  # acabou de ser salvo na linha anterior

    return SuccessResponse(
        message="Arquivo anexado com sucesso.",
        data=AiUploadResponse(
            upload_id=upload_id,
            filename=preview["filename"],
            row_count=preview["row_count"],
            headers=preview["headers"],
        ),
    )


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
