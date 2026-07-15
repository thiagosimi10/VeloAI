import uuid
from contextlib import asynccontextmanager
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from veloai_shared.exceptions import NotFoundError

from app.modules.services.schemas.service import (
    CreateServiceRequest,
    ServiceFilterParams,
    UpdateServiceRequest,
)
from app.modules.services.use_cases.create_service_use_case import CreateServiceUseCase
from app.modules.services.use_cases.delete_service_use_case import DeleteServiceUseCase
from app.modules.services.use_cases.get_service_use_case import GetServiceUseCase
from app.modules.services.use_cases.list_services_use_case import ListServicesUseCase
from app.modules.services.use_cases.update_service_use_case import UpdateServiceUseCase


def _connection_manager_with_session(session: AsyncMock) -> MagicMock:
    @asynccontextmanager
    async def _session_context(*_args: object, **_kwargs: object):
        yield session

    manager = MagicMock()
    manager.session_for_tenant = MagicMock(side_effect=_session_context)
    return manager


def _build_service_mock(**overrides: object) -> MagicMock:
    service = MagicMock()
    service.id = overrides.get("id", uuid.uuid4())
    service.category_id = overrides.get("category_id")
    service.code = overrides.get("code", "S000001")
    service.name = overrides.get("name", "Formatação de Computador")
    service.description = None
    service.estimated_time = overrides.get("estimated_time", 60)
    service.price = overrides.get("price", Decimal("180.00"))
    service.active = overrides.get("active", True)
    from datetime import UTC, datetime

    service.created_at = overrides.get("created_at") or datetime.now(UTC)
    service.updated_at = overrides.get("updated_at") or datetime.now(UTC)
    return service


async def test_list_services_computes_pagination_meta() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = ListServicesUseCase(connection_manager=connection_manager)

    service = _build_service_mock()
    with patch(
        "app.modules.services.use_cases.list_services_use_case.ServiceRepository"
    ) as repo_cls:
        repo_cls.return_value.list = AsyncMock(return_value=([service], 25))

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            filters=ServiceFilterParams(page=1, page_size=10),
        )

    assert result.meta.total == 25
    assert result.meta.pages == 3
    assert len(result.items) == 1
    assert result.items[0].code == "S000001"


async def test_get_service_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = GetServiceUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.services.use_cases.get_service_use_case.ServiceRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(), database_name="tenant_abc", service_id=uuid.uuid4()
            )


async def test_create_service_generates_sequential_code() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CreateServiceUseCase(connection_manager=connection_manager)
    payload = CreateServiceRequest(name="Formatação de Computador", price=Decimal("180.00"))

    async def _fake_create(service: object) -> object:
        # Simula o que `session.flush()` faria de verdade: preencher os campos que só
        # existem após o INSERT (id via default Python, created_at/updated_at via
        # server_default) — sem isso, `ServiceResponse.model_validate` falharia.
        from datetime import UTC, datetime

        service.id = uuid.uuid4()  # type: ignore[attr-defined]
        service.created_at = datetime.now(UTC)  # type: ignore[attr-defined]
        service.updated_at = datetime.now(UTC)  # type: ignore[attr-defined]
        return service

    with (
        patch(
            "app.modules.services.use_cases.create_service_use_case.ServiceRepository"
        ) as repo_cls,
        patch(
            "app.modules.services.use_cases.create_service_use_case.record_audit_log",
            AsyncMock(),
        ),
    ):
        repo_cls.return_value.count_all = AsyncMock(return_value=4)
        repo_cls.return_value.create = AsyncMock(side_effect=_fake_create)

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            payload=payload,
        )

    assert result.code == "S000005"


async def test_create_service_rejects_nonexistent_category() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CreateServiceUseCase(connection_manager=connection_manager)
    payload = CreateServiceRequest(
        name="Formatação de Computador", price=Decimal("180.00"), category_id=uuid.uuid4()
    )

    with patch(
        "app.modules.services.use_cases.create_service_use_case.GetCategoryUseCase"
    ) as get_category_cls:
        get_category_cls.return_value.execute = AsyncMock(
            side_effect=NotFoundError("Categoria não encontrada.", code="CATEGORY_NOT_FOUND")
        )

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                payload=payload,
            )


async def test_update_service_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = UpdateServiceUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.services.use_cases.update_service_use_case.ServiceRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                service_id=uuid.uuid4(),
                payload=UpdateServiceRequest(name="Novo Nome"),
            )


async def test_delete_service_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = DeleteServiceUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.services.use_cases.delete_service_use_case.ServiceRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                service_id=uuid.uuid4(),
            )
