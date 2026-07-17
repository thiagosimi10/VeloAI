"""Cliente Qdrant (RAG — Fase 15), conforme 04-MULTI-TENANCY.md ("Cada empresa
possuirá sua própria Collection"). Infraestrutura cross-cutting (mesmo nível de
`app/core/storage.py`) — indexa/busca só na Collection do tenant corrente
(`veloai_shared.qdrant.collection_name_for_tenant`), nunca em outra: isolamento real
por Collection, não lógico por coluna."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from functools import lru_cache

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue, PointStruct
from veloai_shared.qdrant import collection_name_for_tenant

from app.core.config import get_settings


@dataclass(frozen=True)
class KnowledgeChunk:
    document_id: uuid.UUID
    chunk_index: int
    content: str
    vector: list[float]


@dataclass(frozen=True)
class KnowledgeSearchMatch:
    document_id: uuid.UUID
    chunk_index: int
    content: str
    score: float


class QdrantClient:
    def __init__(self, *, client: AsyncQdrantClient) -> None:
        self._client = client

    async def upsert_chunks(self, tenant_id: uuid.UUID, chunks: list[KnowledgeChunk]) -> None:
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=chunk.vector,
                payload={
                    "document_id": str(chunk.document_id),
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                },
            )
            for chunk in chunks
        ]
        await self._client.upsert(
            collection_name=collection_name_for_tenant(tenant_id), points=points
        )

    async def search(
        self, tenant_id: uuid.UUID, query_vector: list[float], *, limit: int = 5
    ) -> list[KnowledgeSearchMatch]:
        results = await self._client.query_points(
            collection_name=collection_name_for_tenant(tenant_id),
            query=query_vector,
            limit=limit,
        )
        return [
            KnowledgeSearchMatch(
                document_id=uuid.UUID(point.payload["document_id"]),
                chunk_index=point.payload["chunk_index"],
                content=point.payload["content"],
                score=point.score,
            )
            for point in results.points
        ]

    async def delete_document(self, tenant_id: uuid.UUID, document_id: uuid.UUID) -> None:
        await self._client.delete(
            collection_name=collection_name_for_tenant(tenant_id),
            points_selector=Filter(
                must=[
                    FieldCondition(key="document_id", match=MatchValue(value=str(document_id)))
                ]
            ),
        )

    async def is_reachable(self) -> bool:
        try:
            await self._client.get_collections()
            return True
        except Exception:  # noqa: BLE001 - readiness apenas reporta indisponibilidade
            return False


@lru_cache
def get_qdrant_client() -> QdrantClient:
    """Retorna a instância única (cacheada) de `QdrantClient`, mesmo padrão de
    `get_settings()`/`get_storage_client()`."""

    settings = get_settings()
    return QdrantClient(client=AsyncQdrantClient(url=settings.qdrant_url))
