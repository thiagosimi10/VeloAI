"""Caso de uso: excluir um item da Base de Conhecimento. Remove do Qdrant PRIMEIRO, só
então marca a linha do Postgres como excluída — nunca a ordem inversa (mesmo critério
de Anexos: nunca deixar uma linha ativa apontando para um índice já removido)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.core.qdrant_client import QdrantClient
from app.modules.knowledge.repositories.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)


class DeleteKnowledgeDocumentUseCase:
    def __init__(
        self, *, connection_manager: TenantConnectionManager, qdrant_client: QdrantClient
    ) -> None:
        self._connections = connection_manager
        self._qdrant = qdrant_client

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        document_id: uuid.UUID,
    ) -> None:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = KnowledgeDocumentRepository(session)
            document = await repository.get_by_id(document_id)
            if document is None:
                raise NotFoundError(
                    "Documento não encontrado.", code="KNOWLEDGE_DOCUMENT_NOT_FOUND"
                )

            before = {"id": str(document.id), "title": document.title}

            await self._qdrant.delete_document(tenant_id, document_id)
            await repository.soft_delete(document)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="KNOWLEDGE_DOCUMENT_DELETED",
                resource="knowledge_documents",
                before=before,
            )
            await session.commit()
