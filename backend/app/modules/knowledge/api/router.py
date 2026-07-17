"""Controller do módulo de Base de Conhecimento (RAG — Fase 15). Responsabilidade:
receber requisição, validar permissão via `require_permission` e delegar ao Use Case —
nunca conter regra de negócio (00-AI-CONSTITUTION.md)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from veloai_shared.responses import SuccessResponse

from app.core.ai_gateway_client import AIGatewayClient, get_ai_gateway_client
from app.core.database import TenantConnectionManager, get_tenant_connection_manager
from app.core.dependencies import CurrentUser, require_permission
from app.core.qdrant_client import QdrantClient, get_qdrant_client
from app.modules.knowledge.permissions import (
    KNOWLEDGE_CREATE,
    KNOWLEDGE_DELETE,
    KNOWLEDGE_VIEW,
)
from app.modules.knowledge.schemas.knowledge import (
    CreateKnowledgeDocumentRequest,
    KnowledgeDocumentFilterParams,
    KnowledgeDocumentResponse,
)
from app.modules.knowledge.use_cases.create_knowledge_document_use_case import (
    CreateKnowledgeDocumentUseCase,
)
from app.modules.knowledge.use_cases.delete_knowledge_document_use_case import (
    DeleteKnowledgeDocumentUseCase,
)
from app.modules.knowledge.use_cases.list_knowledge_documents_use_case import (
    ListKnowledgeDocumentsUseCase,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("")
async def list_knowledge_documents(
    filters: KnowledgeDocumentFilterParams = Depends(),
    current_user: CurrentUser = Depends(require_permission(KNOWLEDGE_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[KnowledgeDocumentResponse]]:
    use_case = ListKnowledgeDocumentsUseCase(connection_manager=connection_manager)
    result = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        filters=filters,
    )
    return SuccessResponse(
        message="Base de conhecimento listada com sucesso.", data=result.items, meta=result.meta
    )


@router.post("", status_code=201)
async def create_knowledge_document(
    payload: CreateKnowledgeDocumentRequest,
    current_user: CurrentUser = Depends(require_permission(KNOWLEDGE_CREATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
    ai_gateway_client: AIGatewayClient = Depends(get_ai_gateway_client),
    qdrant_client: QdrantClient = Depends(get_qdrant_client),
) -> SuccessResponse[KnowledgeDocumentResponse]:
    use_case = CreateKnowledgeDocumentUseCase(
        connection_manager=connection_manager,
        ai_gateway_client=ai_gateway_client,
        qdrant_client=qdrant_client,
    )
    document = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        payload=payload,
    )
    return SuccessResponse(message="Documento adicionado com sucesso.", data=document)


@router.delete("/{document_id}")
async def delete_knowledge_document(
    document_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(KNOWLEDGE_DELETE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
    qdrant_client: QdrantClient = Depends(get_qdrant_client),
) -> SuccessResponse[dict[str, str]]:
    use_case = DeleteKnowledgeDocumentUseCase(
        connection_manager=connection_manager, qdrant_client=qdrant_client
    )
    await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        document_id=document_id,
    )
    return SuccessResponse(message="Documento removido com sucesso.", data={})
