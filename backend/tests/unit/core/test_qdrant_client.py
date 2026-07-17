import uuid
from unittest.mock import AsyncMock, MagicMock

from veloai_shared.qdrant import collection_name_for_tenant

from app.core.qdrant_client import KnowledgeChunk, QdrantClient


def _build_client() -> tuple[QdrantClient, MagicMock]:
    raw_client = MagicMock()
    raw_client.upsert = AsyncMock()
    raw_client.query_points = AsyncMock()
    raw_client.delete = AsyncMock()
    raw_client.get_collections = AsyncMock()
    return QdrantClient(client=raw_client), raw_client


async def test_upsert_chunks_sends_points_to_the_tenant_collection() -> None:
    client, raw_client = _build_client()
    tenant_id = uuid.uuid4()
    document_id = uuid.uuid4()
    chunks = [
        KnowledgeChunk(document_id=document_id, chunk_index=0, content="chunk um", vector=[0.1]),
        KnowledgeChunk(
            document_id=document_id, chunk_index=1, content="chunk dois", vector=[0.2]
        ),
    ]

    await client.upsert_chunks(tenant_id, chunks)

    raw_client.upsert.assert_awaited_once()
    call_kwargs = raw_client.upsert.call_args.kwargs
    assert call_kwargs["collection_name"] == collection_name_for_tenant(tenant_id)
    points = call_kwargs["points"]
    assert len(points) == 2
    assert points[0].payload["document_id"] == str(document_id)
    assert points[0].payload["chunk_index"] == 0
    assert points[0].payload["content"] == "chunk um"
    assert points[0].vector == [0.1]


async def test_search_returns_matches_from_query_points() -> None:
    client, raw_client = _build_client()
    tenant_id = uuid.uuid4()
    document_id = uuid.uuid4()

    point = MagicMock()
    point.payload = {"document_id": str(document_id), "chunk_index": 0, "content": "trecho"}
    point.score = 0.87
    response = MagicMock()
    response.points = [point]
    raw_client.query_points.return_value = response

    matches = await client.search(tenant_id, [0.1, 0.2], limit=5)

    assert len(matches) == 1
    assert matches[0].document_id == document_id
    assert matches[0].content == "trecho"
    assert matches[0].score == 0.87
    call_kwargs = raw_client.query_points.call_args.kwargs
    assert call_kwargs["collection_name"] == collection_name_for_tenant(tenant_id)
    assert call_kwargs["limit"] == 5


async def test_delete_document_targets_the_tenant_collection() -> None:
    client, raw_client = _build_client()
    tenant_id = uuid.uuid4()
    document_id = uuid.uuid4()

    await client.delete_document(tenant_id, document_id)

    raw_client.delete.assert_awaited_once()
    call_kwargs = raw_client.delete.call_args.kwargs
    assert call_kwargs["collection_name"] == collection_name_for_tenant(tenant_id)


async def test_is_reachable_true_when_get_collections_succeeds() -> None:
    client, _raw_client = _build_client()

    assert await client.is_reachable() is True


async def test_is_reachable_false_when_get_collections_raises() -> None:
    client, raw_client = _build_client()
    raw_client.get_collections.side_effect = RuntimeError("connection refused")

    assert await client.is_reachable() is False
