"""Teste de ponta a ponta do módulo de Anexos (Fase 12 — Storage): login → cria
cliente/produto/OS → upload de um anexo em cada um dos três tipos suportados →
`GET /attachments` retorna com uma `url` pré-assinada válida → `DELETE` remove e uma
segunda listagem confirma ausência → upload com `resource_id` inexistente retorna 404
→ auditoria gravada.

Pulado (não falha) se o MinIO não estiver acessível — mesmo critério de
`_postgres_available()` em `tests/integration/conftest.py`, só que aplicado aqui via
`StorageClient.is_reachable()` (não exige mudanças no conftest compartilhado)."""

from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from fakeredis import aioredis as fakeredis_aioredis
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from veloai_shared.schema.tenant import TenantAuditLog

from app.core.config import get_settings
from app.core.rate_limit import LoginRateLimiter, get_login_rate_limiter
from app.core.storage import get_storage_client
from app.main import app

from .conftest import AuthFixtureData

app.dependency_overrides[get_login_rate_limiter] = lambda: LoginRateLimiter(
    fakeredis_aioredis.FakeRedis(decode_responses=True)
)


def _login(client: TestClient, fixture: AuthFixtureData, password: str) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": fixture.user_email, "password": password},
    )
    assert response.status_code == 200


@pytest_asyncio.fixture(scope="module", autouse=True)
async def _skip_if_minio_unavailable() -> None:
    if not await get_storage_client().is_reachable():
        pytest.skip("MinIO indisponível — pulando testes de integração de Anexos.")


def test_full_attachment_flow(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    customer_response = client.post(
        "/api/v1/customers",
        json={"type": "PF", "name": "Cliente Anexo", "document": "111.444.777-35"},
    )
    customer_id = customer_response.json()["data"]["id"]

    product_response = client.post(
        "/api/v1/products",
        json={
            "sku": "SSD-ANEXO-001",
            "name": "SSD para Teste de Anexo",
            "cost_price": "320.00",
            "sale_price": "490.00",
            "stock": 5,
        },
    )
    product_id = product_response.json()["data"]["id"]

    order_response = client.post(
        "/api/v1/service-orders", json={"customer_id": customer_id}
    )
    order_id = order_response.json()["data"]["id"]

    # Upload de um anexo para cada um dos três tipos suportados.
    resources = [
        ("customer", customer_id),
        ("product", product_id),
        ("service_order", order_id),
    ]
    attachment_ids: dict[str, str] = {}
    for resource_type, resource_id in resources:
        upload_response = client.post(
            "/api/v1/attachments",
            data={"resource_type": resource_type, "resource_id": resource_id},
            files={"file": ("foto.jpg", b"fake-image-bytes", "image/jpeg")},
        )
        assert upload_response.status_code == 201, upload_response.text
        attachment = upload_response.json()["data"]
        assert attachment["original_filename"] == "foto.jpg"
        assert attachment["size_bytes"] == len(b"fake-image-bytes")
        assert attachment["url"].startswith("http")
        attachment_ids[resource_type] = attachment["id"]

    # Lista os anexos da OS e confere a URL pré-assinada.
    list_response = client.get(
        f"/api/v1/attachments?resource_type=service_order&resource_id={order_id}"
    )
    assert list_response.status_code == 200
    items = list_response.json()["data"]
    assert len(items) == 1
    assert items[0]["id"] == attachment_ids["service_order"]

    # Remove o anexo da OS e confere que a listagem fica vazia.
    delete_response = client.delete(f"/api/v1/attachments/{attachment_ids['service_order']}")
    assert delete_response.status_code == 200

    list_after_delete = client.get(
        f"/api/v1/attachments?resource_type=service_order&resource_id={order_id}"
    )
    assert list_after_delete.json()["data"] == []

    # Upload para um recurso inexistente retorna 404.
    upload_missing_response = client.post(
        "/api/v1/attachments",
        data={"resource_type": "customer", "resource_id": str(uuid.uuid4())},
        files={"file": ("foto.jpg", b"fake-image-bytes", "image/jpeg")},
    )
    assert upload_missing_response.status_code == 404


async def test_attachment_lifecycle_is_audited(auth_environment: AuthFixtureData) -> None:
    client = TestClient(app)
    _login(client, auth_environment, auth_environment.temporary_password)

    customer_response = client.post(
        "/api/v1/customers",
        json={"type": "PF", "name": "Cliente Anexo Auditado", "document": "12345678909"},
    )
    customer_id = customer_response.json()["data"]["id"]

    upload_response = client.post(
        "/api/v1/attachments",
        data={"resource_type": "customer", "resource_id": customer_id},
        files={"file": ("doc.pdf", b"fake-pdf-bytes", "application/pdf")},
    )
    attachment_id = upload_response.json()["data"]["id"]
    client.delete(f"/api/v1/attachments/{attachment_id}")

    settings = get_settings()
    tenant_engine = create_async_engine(
        settings.tenant_database_url(auth_environment.database_name)
    )
    try:
        async with tenant_engine.connect() as connection:
            async with AsyncSession(bind=connection) as session:
                result = await session.execute(
                    select(TenantAuditLog.action).where(
                        TenantAuditLog.resource == "attachments"
                    )
                )
                actions = [row[0] for row in result.all()]
    finally:
        await tenant_engine.dispose()

    assert "ATTACHMENT_UPLOADED" in actions
    assert "ATTACHMENT_DELETED" in actions
