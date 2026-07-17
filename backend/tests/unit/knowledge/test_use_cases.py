import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from veloai_shared.exceptions import NotFoundError

from app.core.qdrant_client import KnowledgeSearchMatch
from app.modules.knowledge.schemas.knowledge import (
    CreateKnowledgeDocumentRequest,
    KnowledgeDocumentFilterParams,
)
from app.modules.knowledge.use_cases._helpers import chunk_text
from app.modules.knowledge.use_cases.create_knowledge_document_use_case import (
    CreateKnowledgeDocumentUseCase,
)
from app.modules.knowledge.use_cases.delete_knowledge_document_use_case import (
    DeleteKnowledgeDocumentUseCase,
)
from app.modules.knowledge.use_cases.list_knowledge_documents_use_case import (
    ListKnowledgeDocumentsUseCase,
)
from app.modules.knowledge.use_cases.search_knowledge_use_case import SearchKnowledgeUseCase


def _connection_manager_with_session(session: AsyncMock) -> MagicMock:
    @asynccontextmanager
    async def _session_context(*_args: object, **_kwargs: object):
        yield session

    manager = MagicMock()
    manager.session_for_tenant = MagicMock(side_effect=_session_context)
    return manager


def test_chunk_text_returns_single_chunk_when_content_fits() -> None:
    assert chunk_text("conteúdo curto") == ["conteúdo curto"]


def test_chunk_text_returns_empty_list_for_blank_content() -> None:
    assert chunk_text("   ") == []


def test_chunk_text_never_produces_tiny_trailing_chunk() -> None:
    content = "a" * 2500

    chunks = chunk_text(content, size=1000, overlap=200)

    assert [len(chunk) for chunk in chunks] == [1000, 1000, 900]


def test_chunk_text_chunks_overlap_by_the_configured_amount() -> None:
    content = "a" * 1200

    chunks = chunk_text(content, size=1000, overlap=200)

    assert len(chunks) == 2
    assert chunks[0][-200:] == chunks[1][:200]


async def test_create_knowledge_document_use_case_persists_and_indexes() -> None:
    session = AsyncMock()
    connection_manager = _connection_manager_with_session(session)
    ai_gateway_client = MagicMock()
    ai_gateway_client.embeddings = AsyncMock(return_value=[[0.1, 0.2], [0.3, 0.4]])
    qdrant_client = MagicMock()
    qdrant_client.upsert_chunks = AsyncMock()

    use_case = CreateKnowledgeDocumentUseCase(
        connection_manager=connection_manager,
        ai_gateway_client=ai_gateway_client,
        qdrant_client=qdrant_client,
    )

    async def _fake_create(document: object) -> object:
        document.id = uuid.uuid4()  # type: ignore[attr-defined]
        document.created_at = datetime.now(UTC)  # type: ignore[attr-defined]
        document.updated_at = datetime.now(UTC)  # type: ignore[attr-defined]
        return document

    with (
        patch(
            "app.modules.knowledge.use_cases.create_knowledge_document_use_case."
            "KnowledgeDocumentRepository"
        ) as repo_cls,
        patch(
            "app.modules.knowledge.use_cases.create_knowledge_document_use_case."
            "record_audit_log",
            AsyncMock(),
        ),
        patch(
            "app.modules.knowledge.use_cases.create_knowledge_document_use_case.chunk_text",
            return_value=["chunk um", "chunk dois"],
        ),
    ):
        repo_cls.return_value.create = AsyncMock(side_effect=_fake_create)
        tenant_id = uuid.uuid4()

        result = await use_case.execute(
            tenant_id=tenant_id,
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            payload=CreateKnowledgeDocumentRequest(
                title="Política de Garantia", content="Conteúdo qualquer da política."
            ),
        )

    assert result.title == "Política de Garantia"
    ai_gateway_client.embeddings.assert_awaited_once_with(["chunk um", "chunk dois"])
    qdrant_client.upsert_chunks.assert_awaited_once()
    call_args = qdrant_client.upsert_chunks.call_args
    assert call_args.args[0] == tenant_id
    chunks_sent = call_args.args[1]
    assert [chunk.content for chunk in chunks_sent] == ["chunk um", "chunk dois"]
    assert [chunk.vector for chunk in chunks_sent] == [[0.1, 0.2], [0.3, 0.4]]
    assert [chunk.chunk_index for chunk in chunks_sent] == [0, 1]


async def test_create_knowledge_document_use_case_skips_indexing_when_no_chunks() -> None:
    session = AsyncMock()
    connection_manager = _connection_manager_with_session(session)
    ai_gateway_client = MagicMock()
    ai_gateway_client.embeddings = AsyncMock()
    qdrant_client = MagicMock()
    qdrant_client.upsert_chunks = AsyncMock()

    use_case = CreateKnowledgeDocumentUseCase(
        connection_manager=connection_manager,
        ai_gateway_client=ai_gateway_client,
        qdrant_client=qdrant_client,
    )

    async def _fake_create(document: object) -> object:
        document.id = uuid.uuid4()  # type: ignore[attr-defined]
        document.created_at = datetime.now(UTC)  # type: ignore[attr-defined]
        document.updated_at = datetime.now(UTC)  # type: ignore[attr-defined]
        return document

    with (
        patch(
            "app.modules.knowledge.use_cases.create_knowledge_document_use_case."
            "KnowledgeDocumentRepository"
        ) as repo_cls,
        patch(
            "app.modules.knowledge.use_cases.create_knowledge_document_use_case."
            "record_audit_log",
            AsyncMock(),
        ),
        patch(
            "app.modules.knowledge.use_cases.create_knowledge_document_use_case.chunk_text",
            return_value=[],
        ),
    ):
        repo_cls.return_value.create = AsyncMock(side_effect=_fake_create)

        await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            payload=CreateKnowledgeDocumentRequest(title="Vazio", content=" "),
        )

    ai_gateway_client.embeddings.assert_not_awaited()
    qdrant_client.upsert_chunks.assert_not_awaited()


async def test_list_knowledge_documents_use_case_returns_paginated_items() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = ListKnowledgeDocumentsUseCase(connection_manager=connection_manager)

    document = MagicMock()
    document.id = uuid.uuid4()
    document.title = "Política de Garantia"
    document.content = "Conteúdo"
    document.created_by = uuid.uuid4()
    document.created_at = datetime.now(UTC)
    document.updated_at = datetime.now(UTC)

    with patch(
        "app.modules.knowledge.use_cases.list_knowledge_documents_use_case."
        "KnowledgeDocumentRepository"
    ) as repo_cls:
        repo_cls.return_value.list = AsyncMock(return_value=([document], 1))

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            filters=KnowledgeDocumentFilterParams(page=1, page_size=20),
        )

    assert len(result.items) == 1
    assert result.items[0].title == "Política de Garantia"
    assert result.meta.total == 1


async def test_delete_knowledge_document_use_case_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    qdrant_client = MagicMock()
    qdrant_client.delete_document = AsyncMock()
    use_case = DeleteKnowledgeDocumentUseCase(
        connection_manager=connection_manager, qdrant_client=qdrant_client
    )

    with patch(
        "app.modules.knowledge.use_cases.delete_knowledge_document_use_case."
        "KnowledgeDocumentRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                document_id=uuid.uuid4(),
            )

    qdrant_client.delete_document.assert_not_awaited()


async def test_delete_knowledge_document_use_case_removes_qdrant_before_postgres() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    qdrant_client = MagicMock()
    use_case = DeleteKnowledgeDocumentUseCase(
        connection_manager=connection_manager, qdrant_client=qdrant_client
    )

    document = MagicMock()
    document.id = uuid.uuid4()
    document.title = "Política de Garantia"

    call_order: list[str] = []
    qdrant_client.delete_document = AsyncMock(
        side_effect=lambda *_args, **_kwargs: call_order.append("qdrant_delete")
    )

    with (
        patch(
            "app.modules.knowledge.use_cases.delete_knowledge_document_use_case."
            "KnowledgeDocumentRepository"
        ) as repo_cls,
        patch(
            "app.modules.knowledge.use_cases.delete_knowledge_document_use_case."
            "record_audit_log",
            AsyncMock(),
        ),
    ):
        repo_cls.return_value.get_by_id = AsyncMock(return_value=document)

        async def _fake_soft_delete(_document: object) -> None:
            call_order.append("postgres_soft_delete")

        repo_cls.return_value.soft_delete = AsyncMock(side_effect=_fake_soft_delete)

        await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            document_id=document.id,
        )

    assert call_order == ["qdrant_delete", "postgres_soft_delete"]


async def test_search_knowledge_use_case_returns_results_with_titles() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    ai_gateway_client = MagicMock()
    ai_gateway_client.embeddings = AsyncMock(return_value=[[0.1, 0.2]])
    qdrant_client = MagicMock()
    document_id = uuid.uuid4()
    qdrant_client.search = AsyncMock(
        return_value=[
            KnowledgeSearchMatch(
                document_id=document_id, chunk_index=0, content="trecho relevante", score=0.87
            )
        ]
    )
    use_case = SearchKnowledgeUseCase(
        connection_manager=connection_manager,
        ai_gateway_client=ai_gateway_client,
        qdrant_client=qdrant_client,
    )

    with patch(
        "app.modules.knowledge.use_cases.search_knowledge_use_case.KnowledgeDocumentRepository"
    ) as repo_cls:
        repo_cls.return_value.get_titles_by_ids = AsyncMock(
            return_value={document_id: "Política de Garantia"}
        )

        results = await use_case.execute(
            tenant_id=uuid.uuid4(), database_name="tenant_abc", query="qual a garantia?"
        )

    assert len(results) == 1
    assert results[0].title == "Política de Garantia"
    assert results[0].content == "trecho relevante"
    assert results[0].score == 0.87
    ai_gateway_client.embeddings.assert_awaited_once_with(["qual a garantia?"])


async def test_search_knowledge_use_case_returns_empty_list_when_no_matches() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    ai_gateway_client = MagicMock()
    ai_gateway_client.embeddings = AsyncMock(return_value=[[0.1, 0.2]])
    qdrant_client = MagicMock()
    qdrant_client.search = AsyncMock(return_value=[])
    use_case = SearchKnowledgeUseCase(
        connection_manager=connection_manager,
        ai_gateway_client=ai_gateway_client,
        qdrant_client=qdrant_client,
    )

    results = await use_case.execute(
        tenant_id=uuid.uuid4(), database_name="tenant_abc", query="pergunta sem resultado"
    )

    assert results == []
