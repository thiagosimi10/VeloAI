"""Caso de uso: buscar semanticamente na Base de Conhecimento — usada pela Tool
`SearchKnowledge` (Fase 14/MCP)."""

from __future__ import annotations

import uuid

from app.core.ai_gateway_client import AIGatewayClient
from app.core.database import TenantConnectionManager
from app.core.qdrant_client import QdrantClient
from app.modules.knowledge.repositories.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)
from app.modules.knowledge.schemas.knowledge import KnowledgeSearchResult

_TOP_K = 5


class SearchKnowledgeUseCase:
    def __init__(
        self,
        *,
        connection_manager: TenantConnectionManager,
        ai_gateway_client: AIGatewayClient,
        qdrant_client: QdrantClient,
    ) -> None:
        self._connections = connection_manager
        self._ai_gateway = ai_gateway_client
        self._qdrant = qdrant_client

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, query: str
    ) -> list[KnowledgeSearchResult]:
        vectors = await self._ai_gateway.embeddings([query])
        matches = await self._qdrant.search(tenant_id, vectors[0], limit=_TOP_K)
        if not matches:
            return []

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            titles = await KnowledgeDocumentRepository(session).get_titles_by_ids(
                [match.document_id for match in matches]
            )

        return [
            KnowledgeSearchResult(
                title=titles.get(match.document_id, "Documento removido"),
                content=match.content,
                score=match.score,
            )
            for match in matches
        ]
