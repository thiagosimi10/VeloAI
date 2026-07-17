"""Cria/remove a Collection Qdrant exclusiva de um tenant, conforme
04-MULTI-TENANCY.md ("Cada empresa possuirá sua própria Collection", passo "Criar
Collection Qdrant" do fluxo de provisionamento). Dimensão 768 e distância Cosine —
dimensão real do modelo `AI_EMBEDDING_MODEL=text-embedding-004`
(03-STACK-TECNOLOGICA.md)."""

from __future__ import annotations

import uuid

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams
from veloai_shared.qdrant import collection_name_for_tenant

from app.core.config import get_settings

_EMBEDDING_VECTOR_SIZE = 768


class QdrantProvisioningService:
    def __init__(self, *, client: AsyncQdrantClient | None = None) -> None:
        self._client = client or AsyncQdrantClient(url=get_settings().qdrant_url)

    async def create_tenant_collection(self, tenant_id: uuid.UUID) -> None:
        await self._client.create_collection(
            collection_name=collection_name_for_tenant(tenant_id),
            vectors_config=VectorParams(size=_EMBEDDING_VECTOR_SIZE, distance=Distance.COSINE),
        )

    async def delete_tenant_collection(self, tenant_id: uuid.UUID) -> None:
        await self._client.delete_collection(collection_name_for_tenant(tenant_id))
