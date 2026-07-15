import uuid
from contextlib import asynccontextmanager
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from veloai_shared.exceptions import ConflictError, NotFoundError, ValidationError

from app.modules.service_orders.schemas.service_order import (
    CloseServiceOrderRequest,
    CreateServiceOrderRequest,
    ServiceOrderFilterParams,
    UpdateServiceOrderRequest,
)
from app.modules.service_orders.schemas.service_order_item import AddServiceOrderItemRequest
from app.modules.service_orders.use_cases.add_service_order_item_use_case import (
    AddServiceOrderItemUseCase,
)
from app.modules.service_orders.use_cases.cancel_service_order_use_case import (
    CancelServiceOrderUseCase,
)
from app.modules.service_orders.use_cases.close_service_order_use_case import (
    CloseServiceOrderUseCase,
)
from app.modules.service_orders.use_cases.create_service_order_use_case import (
    CreateServiceOrderUseCase,
)
from app.modules.service_orders.use_cases.delete_service_order_use_case import (
    DeleteServiceOrderUseCase,
)
from app.modules.service_orders.use_cases.get_service_order_use_case import (
    GetServiceOrderUseCase,
)
from app.modules.service_orders.use_cases.list_service_orders_use_case import (
    ListServiceOrdersUseCase,
)
from app.modules.service_orders.use_cases.remove_service_order_item_use_case import (
    RemoveServiceOrderItemUseCase,
)
from app.modules.service_orders.use_cases.start_service_order_use_case import (
    StartServiceOrderUseCase,
)
from app.modules.service_orders.use_cases.update_service_order_use_case import (
    UpdateServiceOrderUseCase,
)


def _connection_manager_with_session(session: AsyncMock) -> MagicMock:
    @asynccontextmanager
    async def _session_context(*_args: object, **_kwargs: object):
        yield session

    manager = MagicMock()
    manager.session_for_tenant = MagicMock(side_effect=_session_context)
    return manager


def _build_order_mock(**overrides: object) -> MagicMock:
    order = MagicMock()
    order.id = overrides.get("id", uuid.uuid4())
    order.number = overrides.get("number", "OS-2026-000001")
    order.customer_id = overrides.get("customer_id", uuid.uuid4())
    order.technician_id = overrides.get("technician_id")
    order.status = overrides.get("status", "open")
    order.equipment = None
    order.serial_number = None
    order.problem = overrides.get("problem", "Não liga")
    order.diagnosis = None
    order.solution = overrides.get("solution")
    order.total = overrides.get("total", Decimal("0.00"))
    from datetime import UTC, datetime

    order.opened_at = datetime.now(UTC)
    order.finished_at = overrides.get("finished_at")
    # `ServiceOrderResponse.items` não corresponde a nenhum atributo real do modelo
    # SQLAlchemy (ver `use_cases/_helpers.py::to_response`) — como `MagicMock()` "tem"
    # qualquer atributo por padrão (auto-vivificação), simulamos aqui o que
    # `to_response`/`build_order_response` fariam num `ServiceOrder` de verdade:
    # garantir uma lista real antes de validar.
    order.items = overrides.get("items", [])
    return order


def _build_item_mock(**overrides: object) -> MagicMock:
    item = MagicMock()
    item.id = overrides.get("id", uuid.uuid4())
    item.service_order_id = overrides.get("service_order_id", uuid.uuid4())
    item.product_id = overrides.get("product_id")
    item.service_id = overrides.get("service_id")
    item.quantity = overrides.get("quantity", 1)
    item.unit_price = overrides.get("unit_price", Decimal("100.00"))
    item.total = overrides.get("total", Decimal("100.00"))
    return item


# --- create ---------------------------------------------------------------


async def test_create_service_order_generates_sequential_number() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CreateServiceOrderUseCase(connection_manager=connection_manager)
    payload = CreateServiceOrderRequest(customer_id=uuid.uuid4())

    async def _fake_create(order: object) -> object:
        from datetime import UTC, datetime

        # `ServiceOrder(...)` não recebe `status`/`total` no construtor — o
        # `default=` da coluna só é aplicado pelo SQLAlchemy no `flush()` real,
        # que este mock nunca executa; sem isso, `order.status`/`order.total`
        # ficariam `None` e `ServiceOrderResponse.model_validate` falharia.
        order.id = uuid.uuid4()  # type: ignore[attr-defined]
        order.opened_at = datetime.now(UTC)  # type: ignore[attr-defined]
        order.status = "open"  # type: ignore[attr-defined]
        order.total = Decimal("0.00")  # type: ignore[attr-defined]
        return order

    with (
        patch(
            "app.modules.service_orders.use_cases.create_service_order_use_case.GetCustomerUseCase"
        ) as get_customer_cls,
        patch(
            "app.modules.service_orders.use_cases.create_service_order_use_case.ServiceOrderRepository"
        ) as repo_cls,
        patch(
            "app.modules.service_orders.use_cases.create_service_order_use_case.record_audit_log",
            AsyncMock(),
        ),
    ):
        get_customer_cls.return_value.execute = AsyncMock()
        repo_cls.return_value.count_all = AsyncMock(return_value=4)
        repo_cls.return_value.create = AsyncMock(side_effect=_fake_create)

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            payload=payload,
        )

    assert result.number.endswith("-000005")
    assert result.status == "open"


async def test_create_service_order_rejects_nonexistent_customer() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CreateServiceOrderUseCase(connection_manager=connection_manager)
    payload = CreateServiceOrderRequest(customer_id=uuid.uuid4())

    with patch(
        "app.modules.service_orders.use_cases.create_service_order_use_case.GetCustomerUseCase"
    ) as get_customer_cls:
        get_customer_cls.return_value.execute = AsyncMock(
            side_effect=NotFoundError("Cliente não encontrado.", code="CUSTOMER_NOT_FOUND")
        )

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                payload=payload,
            )


# --- get / list -------------------------------------------------------------


async def test_get_service_order_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = GetServiceOrderUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.service_orders.use_cases.get_service_order_use_case.ServiceOrderRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(), database_name="tenant_abc", order_id=uuid.uuid4()
            )


async def test_get_service_order_embeds_items() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = GetServiceOrderUseCase(connection_manager=connection_manager)
    order = _build_order_mock()
    item = _build_item_mock(service_order_id=order.id)

    with (
        patch(
            "app.modules.service_orders.use_cases.get_service_order_use_case.ServiceOrderRepository"
        ) as repo_cls,
        patch(
            "app.modules.service_orders.use_cases.get_service_order_use_case.ServiceOrderItemRepository"
        ) as item_repo_cls,
    ):
        repo_cls.return_value.get_by_id = AsyncMock(return_value=order)
        item_repo_cls.return_value.list_all_by_order = AsyncMock(return_value=[item])

        result = await use_case.execute(
            tenant_id=uuid.uuid4(), database_name="tenant_abc", order_id=order.id
        )

    assert len(result.items) == 1
    assert result.items[0].id == item.id


async def test_list_service_orders_computes_pagination_meta() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = ListServiceOrdersUseCase(connection_manager=connection_manager)
    order = _build_order_mock()

    with patch(
        "app.modules.service_orders.use_cases.list_service_orders_use_case.ServiceOrderRepository"
    ) as repo_cls:
        repo_cls.return_value.list = AsyncMock(return_value=([order], 25))

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            filters=ServiceOrderFilterParams(page=1, page_size=10),
        )

    assert result.meta.total == 25
    assert result.meta.pages == 3
    assert len(result.items) == 1


# --- update / delete ---------------------------------------------------------


async def test_update_service_order_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = UpdateServiceOrderUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.service_orders.use_cases.update_service_order_use_case.ServiceOrderRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                order_id=uuid.uuid4(),
                payload=UpdateServiceOrderRequest(diagnosis="Placa-mãe queimada"),
            )


async def test_delete_service_order_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = DeleteServiceOrderUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.service_orders.use_cases.delete_service_order_use_case.ServiceOrderRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                order_id=uuid.uuid4(),
            )


# --- items -------------------------------------------------------------------


async def test_add_item_uses_catalog_price_when_unit_price_omitted() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = AddServiceOrderItemUseCase(connection_manager=connection_manager)
    order = _build_order_mock(status="open")
    product_id = uuid.uuid4()

    with (
        patch(
            "app.modules.service_orders.use_cases.add_service_order_item_use_case.GetProductUseCase"
        ) as get_product_cls,
        patch(
            "app.modules.service_orders.use_cases.add_service_order_item_use_case.ServiceOrderRepository"
        ) as order_repo_cls,
        patch(
            "app.modules.service_orders.use_cases.add_service_order_item_use_case.ServiceOrderItemRepository"
        ) as item_repo_cls,
        patch(
            "app.modules.service_orders.use_cases.add_service_order_item_use_case.record_audit_log",
            AsyncMock(),
        ),
    ):
        async def _fake_create(item: object) -> object:
            item.id = uuid.uuid4()  # type: ignore[attr-defined]
            return item

        product_response = MagicMock()
        product_response.sale_price = Decimal("490.00")
        get_product_cls.return_value.execute = AsyncMock(return_value=product_response)
        order_repo_cls.return_value.get_by_id = AsyncMock(return_value=order)
        item_repo_cls.return_value.create = AsyncMock(side_effect=_fake_create)
        item_repo_cls.return_value.list_all_by_order = AsyncMock(
            return_value=[_build_item_mock(total=Decimal("490.00"))]
        )

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            order_id=order.id,
            payload=AddServiceOrderItemRequest(product_id=product_id, quantity=1),
        )

    assert result.unit_price == Decimal("490.00")
    assert result.total == Decimal("490.00")


async def test_add_item_rejects_when_order_not_editable() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = AddServiceOrderItemUseCase(connection_manager=connection_manager)
    order = _build_order_mock(status="completed")

    with (
        patch(
            "app.modules.service_orders.use_cases.add_service_order_item_use_case.GetProductUseCase"
        ) as get_product_cls,
        patch(
            "app.modules.service_orders.use_cases.add_service_order_item_use_case.ServiceOrderRepository"
        ) as order_repo_cls,
    ):
        product_response = MagicMock()
        product_response.sale_price = Decimal("490.00")
        get_product_cls.return_value.execute = AsyncMock(return_value=product_response)
        order_repo_cls.return_value.get_by_id = AsyncMock(return_value=order)

        with pytest.raises(ValidationError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                order_id=order.id,
                payload=AddServiceOrderItemRequest(product_id=uuid.uuid4(), quantity=1),
            )


async def test_remove_item_rejects_when_order_not_editable() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = RemoveServiceOrderItemUseCase(connection_manager=connection_manager)
    order = _build_order_mock(status="cancelled")

    with patch(
        "app.modules.service_orders.use_cases.remove_service_order_item_use_case.ServiceOrderRepository"
    ) as order_repo_cls:
        order_repo_cls.return_value.get_by_id = AsyncMock(return_value=order)

        with pytest.raises(ValidationError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                order_id=order.id,
                item_id=uuid.uuid4(),
            )


# --- transitions ---------------------------------------------------------------


async def test_start_service_order_rejects_invalid_transition() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = StartServiceOrderUseCase(connection_manager=connection_manager)
    order = _build_order_mock(status="in_progress")

    with patch(
        "app.modules.service_orders.use_cases.start_service_order_use_case.ServiceOrderRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=order)

        with pytest.raises(ValidationError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                order_id=order.id,
            )


async def test_cancel_service_order_rejects_invalid_transition() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CancelServiceOrderUseCase(connection_manager=connection_manager)
    order = _build_order_mock(status="completed")

    with patch(
        "app.modules.service_orders.use_cases.cancel_service_order_use_case.ServiceOrderRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=order)

        with pytest.raises(ValidationError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                order_id=order.id,
            )


async def test_close_service_order_requires_technician() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CloseServiceOrderUseCase(connection_manager=connection_manager)
    order = _build_order_mock(status="in_progress", technician_id=None)

    with patch(
        "app.modules.service_orders.use_cases.close_service_order_use_case.ServiceOrderRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=order)

        with pytest.raises(ValidationError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                order_id=order.id,
                payload=CloseServiceOrderRequest(),
            )


async def test_close_service_order_consumes_stock_for_product_items() -> None:
    session = AsyncMock()
    connection_manager = _connection_manager_with_session(session)
    use_case = CloseServiceOrderUseCase(connection_manager=connection_manager)
    order = _build_order_mock(status="in_progress", technician_id=uuid.uuid4())
    product_id = uuid.uuid4()
    product_item = _build_item_mock(product_id=product_id, service_order_id=order.id, quantity=2)
    service_item = _build_item_mock(
        service_id=uuid.uuid4(), service_order_id=order.id, quantity=1
    )

    with (
        patch(
            "app.modules.service_orders.use_cases.close_service_order_use_case.ServiceOrderRepository"
        ) as order_repo_cls,
        patch(
            "app.modules.service_orders.use_cases.close_service_order_use_case.ServiceOrderItemRepository"
        ) as item_repo_cls,
        patch(
            "app.modules.service_orders.use_cases.close_service_order_use_case.apply_stock_movement"
        ) as apply_stock_movement_mock,
        patch(
            "app.modules.service_orders.use_cases.close_service_order_use_case.record_audit_log",
            AsyncMock(),
        ),
    ):
        order_repo_cls.return_value.get_by_id = AsyncMock(return_value=order)

        def _apply_update(target: object, data: dict[str, object]) -> object:
            for field, value in data.items():
                setattr(target, field, value)
            return target

        # O mock precisa mutar `order` de verdade — como o `update()` real faz via
        # `setattr` — para que `to_response(order)` reflita `status="completed"`;
        # um `AsyncMock()` sem `side_effect` não alteraria o objeto.
        order_repo_cls.return_value.update = AsyncMock(side_effect=_apply_update)
        item_repo_cls.return_value.list_all_by_order = AsyncMock(
            return_value=[product_item, service_item]
        )

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            order_id=order.id,
            payload=CloseServiceOrderRequest(),
        )

        apply_stock_movement_mock.assert_awaited_once_with(
            session,
            product_id=product_id,
            movement="out",
            quantity=2,
            reason=f"Consumo automático pela Ordem de Serviço {order.number}",
        )
        order_repo_cls.return_value.update.assert_awaited_once()

    assert result.status == "completed"


async def test_close_service_order_propagates_insufficient_stock() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CloseServiceOrderUseCase(connection_manager=connection_manager)
    order = _build_order_mock(status="in_progress", technician_id=uuid.uuid4())
    product_item = _build_item_mock(product_id=uuid.uuid4(), service_order_id=order.id)

    with (
        patch(
            "app.modules.service_orders.use_cases.close_service_order_use_case.ServiceOrderRepository"
        ) as order_repo_cls,
        patch(
            "app.modules.service_orders.use_cases.close_service_order_use_case.ServiceOrderItemRepository"
        ) as item_repo_cls,
        patch(
            "app.modules.service_orders.use_cases.close_service_order_use_case.apply_stock_movement",
            AsyncMock(
                side_effect=ConflictError(
                    "Estoque insuficiente para esta movimentação.", code="STOCK_INSUFFICIENT"
                )
            ),
        ),
    ):
        order_repo_cls.return_value.get_by_id = AsyncMock(return_value=order)
        item_repo_cls.return_value.list_all_by_order = AsyncMock(return_value=[product_item])

        with pytest.raises(ConflictError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                order_id=order.id,
                payload=CloseServiceOrderRequest(),
            )
