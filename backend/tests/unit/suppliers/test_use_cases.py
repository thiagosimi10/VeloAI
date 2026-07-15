import uuid
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from veloai_shared.exceptions import ConflictError, NotFoundError

from app.modules.suppliers.schemas.supplier import (
    CreateSupplierRequest,
    SupplierFilterParams,
    UpdateSupplierRequest,
)
from app.modules.suppliers.use_cases.create_supplier_use_case import CreateSupplierUseCase
from app.modules.suppliers.use_cases.delete_supplier_use_case import DeleteSupplierUseCase
from app.modules.suppliers.use_cases.get_supplier_use_case import GetSupplierUseCase
from app.modules.suppliers.use_cases.list_suppliers_use_case import ListSuppliersUseCase
from app.modules.suppliers.use_cases.update_supplier_use_case import UpdateSupplierUseCase


def _connection_manager_with_session(session: AsyncMock) -> MagicMock:
    @asynccontextmanager
    async def _session_context(*_args: object, **_kwargs: object):
        yield session

    manager = MagicMock()
    manager.session_for_tenant = MagicMock(side_effect=_session_context)
    return manager


def _build_supplier_mock(**overrides: object) -> MagicMock:
    supplier = MagicMock()
    supplier.id = overrides.get("id", uuid.uuid4())
    supplier.code = overrides.get("code", "F000001")
    supplier.type = overrides.get("type", "PJ")
    supplier.name = overrides.get("name", "Tech Distribuidora LTDA")
    supplier.document = overrides.get("document", "12345678000199")
    supplier.state_registration = None
    supplier.municipal_registration = None
    supplier.email = overrides.get("email", "contato@techdistribuidora.test")
    supplier.phone = None
    supplier.mobile = None
    supplier.whatsapp = None
    supplier.zipcode = None
    supplier.street = None
    supplier.number = None
    supplier.district = None
    supplier.city = None
    supplier.state = None
    supplier.country = "Brasil"
    supplier.notes = None
    supplier.active = overrides.get("active", True)
    supplier.created_at = overrides.get("created_at")
    supplier.updated_at = overrides.get("updated_at")
    from datetime import UTC, datetime

    supplier.created_at = supplier.created_at or datetime.now(UTC)
    supplier.updated_at = supplier.updated_at or datetime.now(UTC)
    return supplier


async def test_list_suppliers_computes_pagination_meta() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = ListSuppliersUseCase(connection_manager=connection_manager)

    supplier = _build_supplier_mock()
    with patch(
        "app.modules.suppliers.use_cases.list_suppliers_use_case.SupplierRepository"
    ) as repo_cls:
        repo_cls.return_value.list = AsyncMock(return_value=([supplier], 25))

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            filters=SupplierFilterParams(page=1, page_size=10),
        )

    assert result.meta.total == 25
    assert result.meta.pages == 3
    assert len(result.items) == 1
    assert result.items[0].code == "F000001"


async def test_get_supplier_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = GetSupplierUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.suppliers.use_cases.get_supplier_use_case.SupplierRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(), database_name="tenant_abc", supplier_id=uuid.uuid4()
            )


async def test_create_supplier_rejects_duplicate_document() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CreateSupplierUseCase(connection_manager=connection_manager)
    payload = CreateSupplierRequest(
        type="PJ", name="Tech Distribuidora LTDA", document="12345678000199"
    )

    with patch(
        "app.modules.suppliers.use_cases.create_supplier_use_case.SupplierRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_document = AsyncMock(return_value=_build_supplier_mock())

        with pytest.raises(ConflictError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                payload=payload,
            )


async def test_create_supplier_generates_sequential_code() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CreateSupplierUseCase(connection_manager=connection_manager)
    payload = CreateSupplierRequest(
        type="PJ", name="Tech Distribuidora LTDA", document="12345678000199"
    )

    async def _fake_create(supplier: object) -> object:
        # Simula o que `session.flush()` faria de verdade: preencher os campos que só
        # existem após o INSERT (id via default Python, created_at/updated_at via
        # server_default) — sem isso, `SupplierResponse.model_validate` falharia.
        from datetime import UTC, datetime

        supplier.id = uuid.uuid4()  # type: ignore[attr-defined]
        supplier.created_at = datetime.now(UTC)  # type: ignore[attr-defined]
        supplier.updated_at = datetime.now(UTC)  # type: ignore[attr-defined]
        return supplier

    with (
        patch(
            "app.modules.suppliers.use_cases.create_supplier_use_case.SupplierRepository"
        ) as repo_cls,
        patch(
            "app.modules.suppliers.use_cases.create_supplier_use_case.record_audit_log",
            AsyncMock(),
        ),
    ):
        repo_cls.return_value.get_by_document = AsyncMock(return_value=None)
        repo_cls.return_value.count_all = AsyncMock(return_value=4)
        repo_cls.return_value.create = AsyncMock(side_effect=_fake_create)

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            payload=payload,
        )

    assert result.code == "F000005"


async def test_update_supplier_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = UpdateSupplierUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.suppliers.use_cases.update_supplier_use_case.SupplierRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                supplier_id=uuid.uuid4(),
                payload=UpdateSupplierRequest(name="Novo Nome"),
            )


async def test_delete_supplier_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = DeleteSupplierUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.suppliers.use_cases.delete_supplier_use_case.SupplierRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                supplier_id=uuid.uuid4(),
            )
