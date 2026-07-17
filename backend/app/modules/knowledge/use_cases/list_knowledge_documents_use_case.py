"""Caso de uso: listar a Base de Conhecimento com paginação simples."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from veloai_shared.responses import PaginationMeta

from app.core.database import TenantConnectionManager
from app.modules.knowledge.repositories.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)
from app.modules.knowledge.schemas.knowledge import (
    KnowledgeDocumentFilterParams,
    KnowledgeDocumentResponse,
)


@dataclass(frozen=True)
class ListKnowledgeDocumentsResult:
    items: list[KnowledgeDocumentResponse]
    meta: PaginationMeta


class ListKnowledgeDocumentsUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        filters: KnowledgeDocumentFilterParams,
    ) -> ListKnowledgeDocumentsResult:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            documents, total = await KnowledgeDocumentRepository(session).list(
                page=filters.page, page_size=filters.page_size
            )

        pages = (total + filters.page_size - 1) // filters.page_size if total else 0
        return ListKnowledgeDocumentsResult(
            items=[KnowledgeDocumentResponse.model_validate(document) for document in documents],
            meta=PaginationMeta(
                page=filters.page, page_size=filters.page_size, total=total, pages=pages
            ),
        )
