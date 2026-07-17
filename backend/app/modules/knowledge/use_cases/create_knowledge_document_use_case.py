"""Caso de uso: criar um item da Base de Conhecimento. Grava o registro no Postgres e
indexa de verdade — chunking (sem LangChain) → embeddings reais do Gemini (via AI
Gateway) → upsert no Qdrant, tudo na mesma requisição (sem fila, Fase 15)."""

from __future__ import annotations

import uuid

from veloai_shared.schema.tenant import KnowledgeDocument

from app.core.ai_gateway_client import AIGatewayClient
from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.core.qdrant_client import KnowledgeChunk, QdrantClient
from app.modules.knowledge.repositories.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)
from app.modules.knowledge.schemas.knowledge import (
    CreateKnowledgeDocumentRequest,
    KnowledgeDocumentResponse,
)
from app.modules.knowledge.use_cases._helpers import chunk_text


class CreateKnowledgeDocumentUseCase:
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
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        payload: CreateKnowledgeDocumentRequest,
    ) -> KnowledgeDocumentResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            document = KnowledgeDocument(
                title=payload.title, content=payload.content, created_by=actor_user_id
            )
            await KnowledgeDocumentRepository(session).create(document)
            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="KNOWLEDGE_DOCUMENT_CREATED",
                resource="knowledge_documents",
                after={"id": str(document.id), "title": document.title},
            )
            await session.commit()

            response = KnowledgeDocumentResponse.model_validate(document)

        chunks = chunk_text(payload.content)
        if chunks:
            vectors = await self._ai_gateway.embeddings(chunks)
            knowledge_chunks = [
                KnowledgeChunk(
                    document_id=document.id, chunk_index=index, content=chunk, vector=vector
                )
                for index, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True))
            ]
            await self._qdrant.upsert_chunks(tenant_id, knowledge_chunks)

        return response
