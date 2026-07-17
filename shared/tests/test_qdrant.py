from __future__ import annotations

import uuid

from veloai_shared.qdrant import collection_name_for_tenant


def test_collection_name_for_tenant_is_deterministic() -> None:
    tenant_id = uuid.uuid4()

    assert collection_name_for_tenant(tenant_id) == collection_name_for_tenant(tenant_id)


def test_collection_name_for_tenant_follows_documented_format() -> None:
    tenant_id = uuid.uuid4()

    assert collection_name_for_tenant(tenant_id) == f"tenant_{tenant_id}_vectors"


def test_collection_name_differs_by_tenant() -> None:
    assert collection_name_for_tenant(uuid.uuid4()) != collection_name_for_tenant(uuid.uuid4())
