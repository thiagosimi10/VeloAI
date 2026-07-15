import uuid
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from veloai_shared.exceptions import ConflictError, NotFoundError

from app.modules.customers.schemas.customer import (
    CreateCustomerRequest,
    CustomerFilterParams,
    UpdateCustomerRequest,
)
from app.modules.customers.use_cases.create_customer_use_case import CreateCustomerUseCase
from app.modules.customers.use_cases.delete_customer_use_case import DeleteCustomerUseCase
from app.modules.customers.use_cases.get_customer_use_case import GetCustomerUseCase
from app.modules.customers.use_cases.list_customers_use_case import ListCustomersUseCase
from app.modules.customers.use_cases.update_customer_use_case import UpdateCustomerUseCase


def _connection_manager_with_session(session: AsyncMock) -> MagicMock:
    @asynccontextmanager
    async def _session_context(*_args: object, **_kwargs: object):
        yield session

    manager = MagicMock()
    manager.session_for_tenant = MagicMock(side_effect=_session_context)
    return manager


def _build_customer_mock(**overrides: object) -> MagicMock:
    customer = MagicMock()
    customer.id = overrides.get("id", uuid.uuid4())
    customer.code = overrides.get("code", "C000001")
    customer.type = overrides.get("type", "PF")
    customer.name = overrides.get("name", "João Silva")
    customer.document = overrides.get("document", "12345678901")
    customer.state_registration = None
    customer.municipal_registration = None
    customer.email = overrides.get("email", "joao@empresa.test")
    customer.phone = None
    customer.mobile = None
    customer.whatsapp = None
    customer.zipcode = None
    customer.street = None
    customer.number = None
    customer.district = None
    customer.city = None
    customer.state = None
    customer.country = "Brasil"
    customer.notes = None
    customer.active = overrides.get("active", True)
    customer.created_at = overrides.get("created_at")
    customer.updated_at = overrides.get("updated_at")
    from datetime import UTC, datetime

    customer.created_at = customer.created_at or datetime.now(UTC)
    customer.updated_at = customer.updated_at or datetime.now(UTC)
    return customer


async def test_list_customers_computes_pagination_meta() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = ListCustomersUseCase(connection_manager=connection_manager)

    customer = _build_customer_mock()
    with patch(
        "app.modules.customers.use_cases.list_customers_use_case.CustomerRepository"
    ) as repo_cls:
        repo_cls.return_value.list = AsyncMock(return_value=([customer], 25))

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            filters=CustomerFilterParams(page=1, page_size=10),
        )

    assert result.meta.total == 25
    assert result.meta.pages == 3
    assert len(result.items) == 1
    assert result.items[0].code == "C000001"


async def test_get_customer_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = GetCustomerUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.customers.use_cases.get_customer_use_case.CustomerRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(), database_name="tenant_abc", customer_id=uuid.uuid4()
            )


async def test_create_customer_rejects_duplicate_document() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CreateCustomerUseCase(connection_manager=connection_manager)
    payload = CreateCustomerRequest(type="PF", name="João Silva", document="12345678901")

    with patch(
        "app.modules.customers.use_cases.create_customer_use_case.CustomerRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_document = AsyncMock(return_value=_build_customer_mock())

        with pytest.raises(ConflictError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                payload=payload,
            )


async def test_create_customer_generates_sequential_code() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CreateCustomerUseCase(connection_manager=connection_manager)
    payload = CreateCustomerRequest(type="PF", name="João Silva", document="12345678901")

    async def _fake_create(customer: object) -> object:
        # Simula o que `session.flush()` faria de verdade: preencher os campos que só
        # existem após o INSERT (id via default Python, created_at/updated_at via
        # server_default) — sem isso, `CustomerResponse.model_validate` falharia.
        from datetime import UTC, datetime

        customer.id = uuid.uuid4()  # type: ignore[attr-defined]
        customer.created_at = datetime.now(UTC)  # type: ignore[attr-defined]
        customer.updated_at = datetime.now(UTC)  # type: ignore[attr-defined]
        return customer

    with (
        patch(
            "app.modules.customers.use_cases.create_customer_use_case.CustomerRepository"
        ) as repo_cls,
        patch(
            "app.modules.customers.use_cases.create_customer_use_case.record_audit_log",
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

    assert result.code == "C000005"


async def test_update_customer_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = UpdateCustomerUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.customers.use_cases.update_customer_use_case.CustomerRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                customer_id=uuid.uuid4(),
                payload=UpdateCustomerRequest(name="Novo Nome"),
            )


async def test_delete_customer_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = DeleteCustomerUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.customers.use_cases.delete_customer_use_case.CustomerRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                customer_id=uuid.uuid4(),
            )
