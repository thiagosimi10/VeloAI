"""Teste de ponta a ponta do módulo de Base de Conhecimento (RAG — Fase 15): login →
`POST /knowledge` indexa de verdade (chunking real + upsert real no Qdrant; só o
`AIGatewayClient.embeddings` é substituído por um dependency override, já que chamar o
Gemini de verdade em CI não é desejável) → `GET /knowledge` lista → `DELETE
/knowledge/{id}` remove do Qdrant e do Postgres.

Pulado (não falha) se o Qdrant não estiver acessível — mesmo critério de MinIO em
`test_attachments_flow.py`. Diferente de Anexos (bucket único compartilhado), o Qdrant
usa uma Collection por tenant (04-MULTI-TENANCY.md); como o tenant de teste é seedado
diretamente por `conftest.py` (sem passar pelo Provisioning Service de verdade), este
teste cria e remove a Collection do tenant de teste manualmente."""

from __future__ import annotations

from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fakeredis import aioredis as fakeredis_aioredis
from fastapi.testclient import TestClient
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams
from veloai_shared.qdrant import collection_name_for_tenant

from app.core.ai_gateway_client import get_ai_gateway_client
from app.core.config import get_settings
from app.core.rate_limit import LoginRateLimiter, get_login_rate_limiter
from app.main import app

from .conftest import AuthFixtureData

app.dependency_overrides[get_login_rate_limiter] = lambda: LoginRateLimiter(
    fakeredis_aioredis.FakeRedis(decode_responses=True)
)

_FAKE_VECTOR_SIZE = 3


def _login(client: TestClient, fixture: AuthFixtureData, password: str) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": fixture.user_email, "password": password},
    )
    assert response.status_code == 200


async def _qdrant_available() -> bool:
    client = AsyncQdrantClient(url=get_settings().qdrant_url, timeout=2)
    try:
        await client.get_collections()
    except Exception:  # noqa: BLE001 - qualquer falha de conexão apenas pula os testes
        return False
    finally:
        await client.close()
    return True


@pytest_asyncio.fixture(scope="module", autouse=True)
async def _tenant_qdrant_collection(
    auth_environment: AuthFixtureData,
) -> AsyncIterator[None]:
    if not await _qdrant_available():
        pytest.skip(
            "Qdrant indisponível — pulando testes de integração de Base de Conhecimento."
        )

    client = AsyncQdrantClient(url=get_settings().qdrant_url)
    collection_name = collection_name_for_tenant(auth_environment.tenant_id)
    try:
        await client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=_FAKE_VECTOR_SIZE, distance=Distance.COSINE),
        )
        yield
    finally:
        await client.delete_collection(collection_name)
        await client.close()


def _fake_ai_gateway_client() -> MagicMock:
    client = MagicMock()
    client.embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3]])
    return client


def test_knowledge_document_lifecycle(auth_environment: AuthFixtureData) -> None:
    fake_ai_gateway = _fake_ai_gateway_client()
    app.dependency_overrides[get_ai_gateway_client] = lambda: fake_ai_gateway
    try:
        client = TestClient(app)
        _login(client, auth_environment, auth_environment.temporary_password)

        create_response = client.post(
            "/api/v1/knowledge",
            json={
                "title": "Política de Garantia",
                "content": "Todo produto tem garantia de 90 dias contra defeitos de fabricação.",
            },
        )
        assert create_response.status_code == 201, create_response.text
        document = create_response.json()["data"]
        assert document["title"] == "Política de Garantia"
        fake_ai_gateway.embeddings.assert_awaited_once()

        list_response = client.get("/api/v1/knowledge")
        assert list_response.status_code == 200
        items = list_response.json()["data"]
        assert any(item["id"] == document["id"] for item in items)

        delete_response = client.delete(f"/api/v1/knowledge/{document['id']}")
        assert delete_response.status_code == 200

        list_after_delete = client.get("/api/v1/knowledge")
        remaining_ids = {item["id"] for item in list_after_delete.json()["data"]}
        assert document["id"] not in remaining_ids
    finally:
        del app.dependency_overrides[get_ai_gateway_client]


def test_delete_knowledge_document_returns_404_for_unknown_id(
    auth_environment: AuthFixtureData,
) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    response = client.delete("/api/v1/knowledge/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
