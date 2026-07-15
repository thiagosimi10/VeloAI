"""Caso de uso: listar o histórico de uso de IA do tenant (auditoria/depuração), com
paginação simples."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from veloai_shared.responses import PaginationMeta

from app.core.database import TenantConnectionManager
from app.modules.ai.repositories.ai_conversation_repository import AiConversationRepository
from app.modules.ai.schemas.ai import AiConversationFilterParams, AiConversationResponse


@dataclass(frozen=True)
class ListAiConversationsResult:
    items: list[AiConversationResponse]
    meta: PaginationMeta


class ListAiConversationsUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        filters: AiConversationFilterParams,
    ) -> ListAiConversationsResult:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            conversations, total = await AiConversationRepository(session).list_by_tenant(
                page=filters.page, page_size=filters.page_size
            )

        pages = (total + filters.page_size - 1) // filters.page_size if total else 0
        return ListAiConversationsResult(
            items=[
                AiConversationResponse.model_validate(conversation)
                for conversation in conversations
            ],
            meta=PaginationMeta(
                page=filters.page, page_size=filters.page_size, total=total, pages=pages
            ),
        )
