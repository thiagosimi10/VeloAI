import uuid
from unittest.mock import AsyncMock, MagicMock

from qdrant_client.models import Distance
from veloai_shared.qdrant import collection_name_for_tenant

from app.services.qdrant_provisioning_service import QdrantProvisioningService


def _build_service() -> tuple[QdrantProvisioningService, MagicMock]:
    client = MagicMock()
    client.create_collection = AsyncMock()
    client.delete_collection = AsyncMock()
    service = QdrantProvisioningService(client=client)
    return service, client


async def test_create_tenant_collection_uses_documented_name_and_vector_size() -> None:
    service, client = _build_service()
    tenant_id = uuid.uuid4()

    await service.create_tenant_collection(tenant_id)

    client.create_collection.assert_awaited_once()
    call_kwargs = client.create_collection.call_args.kwargs
    assert call_kwargs["collection_name"] == collection_name_for_tenant(tenant_id)
    assert call_kwargs["vectors_config"].size == 768
    assert call_kwargs["vectors_config"].distance == Distance.COSINE


async def test_delete_tenant_collection_targets_the_right_collection() -> None:
    service, client = _build_service()
    tenant_id = uuid.uuid4()

    await service.delete_tenant_collection(tenant_id)

    client.delete_collection.assert_awaited_once_with(collection_name_for_tenant(tenant_id))
