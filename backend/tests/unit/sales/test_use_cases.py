import uuid
from contextlib import asynccontextmanager
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from veloai_shared.exceptions import ConflictError, NotFoundError, ValidationError

from app.modules.sales.schemas.sale import (
    CreateSaleRequest,
    SaleFilterParams,
    UpdateSaleRequest,
)
from app.modules.sales.schemas.sale_item import AddSaleItemRequest
from app.modules.sales.use_cases.add_sale_item_use_case import AddSaleItemUseCase
from app.modules.sales.use_cases.cancel_sale_use_case import CancelSaleUseCase
from app.modules.sales.use_cases.complete_sale_use_case import CompleteSaleUseCase
from app.modules.sales.use_cases.create_sale_use_case import CreateSaleUseCase
from app.modules.sales.use_cases.get_sale_use_case import GetSaleUseCase
from app.modules.sales.use_cases.list_sales_use_case import ListSalesUseCase
from app.modules.sales.use_cases.remove_sale_item_use_case import RemoveSaleItemUseCase
from app.modules.sales.use_cases.update_sale_use_case import UpdateSaleUseCase


def _connection_manager_with_session(session: AsyncMock) -> MagicMock:
    @asynccontextmanager
    async def _session_context(*_args: object, **_kwargs: object):
        yield session

    manager = MagicMock()
    manager.session_for_tenant = MagicMock(side_effect=_session_context)
    return manager


def _build_sale_mock(**overrides: object) -> MagicMock:
    sale = MagicMock()
    sale.id = overrides.get("id", uuid.uuid4())
    sale.customer_id = overrides.get("customer_id", uuid.uuid4())
    sale.status = overrides.get("status", "open")
    sale.payment_method = overrides.get("payment_method")
    sale.discount = overrides.get("discount", Decimal("0.00"))
    sale.total = overrides.get("total", Decimal("0.00"))
    from datetime import UTC, datetime

    sale.created_at = datetime.now(UTC)
    # `SaleResponse.items` não corresponde a nenhum atributo real do modelo SQLAlchemy
    # (ver `use_cases/_helpers.py::to_response`) — como `MagicMock()` "tem" qualquer
    # atributo por padrão (auto-vivificação), simulamos aqui o que
    # `to_response`/`build_sale_response` fariam num `Sale` de verdade: garantir uma
    # lista real antes de validar.
    sale.items = overrides.get("items", [])
    return sale


def _build_item_mock(**overrides: object) -> MagicMock:
    item = MagicMock()
    item.id = overrides.get("id", uuid.uuid4())
    item.sale_id = overrides.get("sale_id", uuid.uuid4())
    item.product_id = overrides.get("product_id", uuid.uuid4())
    item.quantity = overrides.get("quantity", 1)
    item.unit_price = overrides.get("unit_price", Decimal("100.00"))
    return item


# --- create ---------------------------------------------------------------


async def test_create_sale_use_case_creates_open_sale() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CreateSaleUseCase(connection_manager=connection_manager)
    payload = CreateSaleRequest(customer_id=uuid.uuid4(), payment_method="pix")

    async def _fake_create(sale: object) -> object:
        from datetime import UTC, datetime

        # `Sale(...)` não recebe `status`/`discount`/`total` no construtor — o
        # `default=` da coluna só é aplicado pelo SQLAlchemy no `flush()` real, que
        # este mock nunca executa; sem isso, esses campos ficariam `None` e
        # `SaleResponse.model_validate` falharia (todos são `Decimal`/`Literal`
        # obrigatórios, não aceitam `None`).
        sale.id = uuid.uuid4()  # type: ignore[attr-defined]
        sale.created_at = datetime.now(UTC)  # type: ignore[attr-defined]
        sale.status = "open"  # type: ignore[attr-defined]
        sale.discount = Decimal("0.00")  # type: ignore[attr-defined]
        sale.total = Decimal("0.00")  # type: ignore[attr-defined]
        return sale

    with (
        patch(
            "app.modules.sales.use_cases.create_sale_use_case.GetCustomerUseCase"
        ) as get_customer_cls,
        patch(
            "app.modules.sales.use_cases.create_sale_use_case.SaleRepository"
        ) as repo_cls,
        patch(
            "app.modules.sales.use_cases.create_sale_use_case.record_audit_log", AsyncMock()
        ),
    ):
        get_customer_cls.return_value.execute = AsyncMock()
        repo_cls.return_value.create = AsyncMock(side_effect=_fake_create)

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            payload=payload,
        )

    assert result.status == "open"
    assert result.payment_method == "pix"


async def test_create_sale_rejects_nonexistent_customer() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CreateSaleUseCase(connection_manager=connection_manager)
    payload = CreateSaleRequest(customer_id=uuid.uuid4())

    with patch(
        "app.modules.sales.use_cases.create_sale_use_case.GetCustomerUseCase"
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


async def test_get_sale_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = GetSaleUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.sales.use_cases.get_sale_use_case.SaleRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(), database_name="tenant_abc", sale_id=uuid.uuid4()
            )


async def test_get_sale_embeds_items() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = GetSaleUseCase(connection_manager=connection_manager)
    sale = _build_sale_mock()
    item = _build_item_mock(sale_id=sale.id)

    with (
        patch("app.modules.sales.use_cases.get_sale_use_case.SaleRepository") as repo_cls,
        patch(
            "app.modules.sales.use_cases.get_sale_use_case.SaleItemRepository"
        ) as item_repo_cls,
    ):
        repo_cls.return_value.get_by_id = AsyncMock(return_value=sale)
        item_repo_cls.return_value.list_all_by_sale = AsyncMock(return_value=[item])

        result = await use_case.execute(
            tenant_id=uuid.uuid4(), database_name="tenant_abc", sale_id=sale.id
        )

    assert len(result.items) == 1
    assert result.items[0].id == item.id


async def test_list_sales_computes_pagination_meta() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = ListSalesUseCase(connection_manager=connection_manager)
    sale = _build_sale_mock()

    with patch(
        "app.modules.sales.use_cases.list_sales_use_case.SaleRepository"
    ) as repo_cls:
        repo_cls.return_value.list = AsyncMock(return_value=([sale], 25))

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            filters=SaleFilterParams(page=1, page_size=10),
        )

    assert result.meta.total == 25
    assert result.meta.pages == 3
    assert len(result.items) == 1


# --- update ------------------------------------------------------------------


async def test_update_sale_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = UpdateSaleUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.sales.use_cases.update_sale_use_case.SaleRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                sale_id=uuid.uuid4(),
                payload=UpdateSaleRequest(payment_method="pix"),
            )


async def test_update_sale_rejects_when_not_open() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = UpdateSaleUseCase(connection_manager=connection_manager)
    sale = _build_sale_mock(status="paid")

    with patch(
        "app.modules.sales.use_cases.update_sale_use_case.SaleRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=sale)

        with pytest.raises(ValidationError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                sale_id=sale.id,
                payload=UpdateSaleRequest(discount=Decimal("10.00")),
            )


async def test_update_sale_recalculates_total_when_discount_changes() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = UpdateSaleUseCase(connection_manager=connection_manager)
    sale = _build_sale_mock(status="open")
    item = _build_item_mock(sale_id=sale.id, quantity=2, unit_price=Decimal("100.00"))

    with (
        patch("app.modules.sales.use_cases.update_sale_use_case.SaleRepository") as repo_cls,
        patch(
            "app.modules.sales.use_cases.update_sale_use_case.SaleItemRepository"
        ) as item_repo_cls,
        patch(
            "app.modules.sales.use_cases.update_sale_use_case.record_audit_log", AsyncMock()
        ),
    ):
        repo_cls.return_value.get_by_id = AsyncMock(return_value=sale)
        repo_cls.return_value.update = AsyncMock()
        item_repo_cls.return_value.list_all_by_sale = AsyncMock(return_value=[item])

        def _apply_update(target: object, data: dict[str, object]) -> object:
            for field, value in data.items():
                setattr(target, field, value)
            return target

        repo_cls.return_value.update.side_effect = _apply_update

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            sale_id=sale.id,
            payload=UpdateSaleRequest(discount=Decimal("20.00")),
        )

    assert result.total == Decimal("180.00")


# --- items -------------------------------------------------------------------


async def test_add_item_uses_catalog_price_when_unit_price_omitted() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = AddSaleItemUseCase(connection_manager=connection_manager)
    sale = _build_sale_mock(status="open")
    product_id = uuid.uuid4()

    with (
        patch(
            "app.modules.sales.use_cases.add_sale_item_use_case.GetProductUseCase"
        ) as get_product_cls,
        patch(
            "app.modules.sales.use_cases.add_sale_item_use_case.SaleRepository"
        ) as sale_repo_cls,
        patch(
            "app.modules.sales.use_cases.add_sale_item_use_case.SaleItemRepository"
        ) as item_repo_cls,
        patch(
            "app.modules.sales.use_cases.add_sale_item_use_case.record_audit_log", AsyncMock()
        ),
    ):
        async def _fake_create(item: object) -> object:
            item.id = uuid.uuid4()  # type: ignore[attr-defined]
            return item

        product_response = MagicMock()
        product_response.sale_price = Decimal("490.00")
        get_product_cls.return_value.execute = AsyncMock(return_value=product_response)
        sale_repo_cls.return_value.get_by_id = AsyncMock(return_value=sale)
        item_repo_cls.return_value.create = AsyncMock(side_effect=_fake_create)
        item_repo_cls.return_value.list_all_by_sale = AsyncMock(
            return_value=[_build_item_mock(unit_price=Decimal("490.00"), quantity=1)]
        )

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            sale_id=sale.id,
            payload=AddSaleItemRequest(product_id=product_id, quantity=1),
        )

    assert result.unit_price == Decimal("490.00")
    assert result.total == Decimal("490.00")


async def test_add_item_rejects_when_sale_not_editable() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = AddSaleItemUseCase(connection_manager=connection_manager)
    sale = _build_sale_mock(status="paid")

    with (
        patch(
            "app.modules.sales.use_cases.add_sale_item_use_case.GetProductUseCase"
        ) as get_product_cls,
        patch(
            "app.modules.sales.use_cases.add_sale_item_use_case.SaleRepository"
        ) as sale_repo_cls,
    ):
        product_response = MagicMock()
        product_response.sale_price = Decimal("490.00")
        get_product_cls.return_value.execute = AsyncMock(return_value=product_response)
        sale_repo_cls.return_value.get_by_id = AsyncMock(return_value=sale)

        with pytest.raises(ValidationError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                sale_id=sale.id,
                payload=AddSaleItemRequest(product_id=uuid.uuid4(), quantity=1),
            )


async def test_remove_item_rejects_when_sale_not_editable() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = RemoveSaleItemUseCase(connection_manager=connection_manager)
    sale = _build_sale_mock(status="cancelled")

    with patch(
        "app.modules.sales.use_cases.remove_sale_item_use_case.SaleRepository"
    ) as sale_repo_cls:
        sale_repo_cls.return_value.get_by_id = AsyncMock(return_value=sale)

        with pytest.raises(ValidationError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                sale_id=sale.id,
                item_id=uuid.uuid4(),
            )


# --- transitions ---------------------------------------------------------------


async def test_cancel_sale_rejects_invalid_transition() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CancelSaleUseCase(connection_manager=connection_manager)
    sale = _build_sale_mock(status="paid")

    with patch(
        "app.modules.sales.use_cases.cancel_sale_use_case.SaleRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=sale)

        with pytest.raises(ValidationError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                sale_id=sale.id,
            )


async def test_complete_sale_rejects_invalid_transition() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CompleteSaleUseCase(connection_manager=connection_manager)
    sale = _build_sale_mock(status="cancelled")

    with patch(
        "app.modules.sales.use_cases.complete_sale_use_case.SaleRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=sale)

        with pytest.raises(ValidationError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                sale_id=sale.id,
            )


async def test_complete_sale_consumes_stock_for_each_item() -> None:
    session = AsyncMock()
    connection_manager = _connection_manager_with_session(session)
    use_case = CompleteSaleUseCase(connection_manager=connection_manager)
    sale = _build_sale_mock(status="open")
    product_id = uuid.uuid4()
    item = _build_item_mock(product_id=product_id, sale_id=sale.id, quantity=3)

    with (
        patch(
            "app.modules.sales.use_cases.complete_sale_use_case.SaleRepository"
        ) as sale_repo_cls,
        patch(
            "app.modules.sales.use_cases.complete_sale_use_case.SaleItemRepository"
        ) as item_repo_cls,
        patch(
            "app.modules.sales.use_cases.complete_sale_use_case.apply_stock_movement"
        ) as apply_stock_movement_mock,
        patch(
            "app.modules.sales.use_cases.complete_sale_use_case.record_audit_log", AsyncMock()
        ),
    ):
        sale_repo_cls.return_value.get_by_id = AsyncMock(return_value=sale)

        def _apply_update(target: object, data: dict[str, object]) -> object:
            for field, value in data.items():
                setattr(target, field, value)
            return target

        # Precisa mutar `sale` de verdade (como o `update()` real faz via `setattr`)
        # para que `to_response(sale)` reflita `status="paid"`.
        sale_repo_cls.return_value.update = AsyncMock(side_effect=_apply_update)
        item_repo_cls.return_value.list_all_by_sale = AsyncMock(return_value=[item])

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            sale_id=sale.id,
        )

        apply_stock_movement_mock.assert_awaited_once_with(
            session,
            product_id=product_id,
            movement="out",
            quantity=3,
            reason=f"Consumo automático pela Venda {sale.id}",
        )
        sale_repo_cls.return_value.update.assert_awaited_once_with(sale, {"status": "paid"})

    assert result.status == "paid"


async def test_complete_sale_propagates_insufficient_stock() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CompleteSaleUseCase(connection_manager=connection_manager)
    sale = _build_sale_mock(status="open")
    item = _build_item_mock(sale_id=sale.id)

    with (
        patch(
            "app.modules.sales.use_cases.complete_sale_use_case.SaleRepository"
        ) as sale_repo_cls,
        patch(
            "app.modules.sales.use_cases.complete_sale_use_case.SaleItemRepository"
        ) as item_repo_cls,
        patch(
            "app.modules.sales.use_cases.complete_sale_use_case.apply_stock_movement",
            AsyncMock(
                side_effect=ConflictError(
                    "Estoque insuficiente para esta movimentação.", code="STOCK_INSUFFICIENT"
                )
            ),
        ),
    ):
        sale_repo_cls.return_value.get_by_id = AsyncMock(return_value=sale)
        item_repo_cls.return_value.list_all_by_sale = AsyncMock(return_value=[item])

        with pytest.raises(ConflictError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                sale_id=sale.id,
            )
