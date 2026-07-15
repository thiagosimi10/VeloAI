import uuid
from contextlib import asynccontextmanager
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from veloai_shared.exceptions import ConflictError, NotFoundError

from app.modules.products.schemas.stock_movement import (
    CreateStockMovementRequest,
    StockMovementFilterParams,
)
from app.modules.products.use_cases.adjust_product_stock_use_case import (
    AdjustProductStockUseCase,
)
from app.modules.products.use_cases.list_stock_movements_use_case import (
    ListStockMovementsUseCase,
)


def _connection_manager_with_session(session: AsyncMock) -> MagicMock:
    @asynccontextmanager
    async def _session_context(*_args: object, **_kwargs: object):
        yield session

    manager = MagicMock()
    manager.session_for_tenant = MagicMock(side_effect=_session_context)
    return manager


def _build_product_mock(**overrides: object) -> MagicMock:
    product = MagicMock()
    product.id = overrides.get("id", uuid.uuid4())
    product.sku = "SSD-KGN-1TB"
    product.stock = overrides.get("stock", 10)
    product.cost_price = Decimal("320.00")
    product.sale_price = Decimal("490.00")
    return product


def _build_movement_mock(**overrides: object) -> MagicMock:
    movement = MagicMock()
    movement.id = overrides.get("id", uuid.uuid4())
    movement.product_id = overrides.get("product_id", uuid.uuid4())
    movement.movement = overrides.get("movement", "in")
    movement.quantity = overrides.get("quantity", 5)
    movement.previous_stock = overrides.get("previous_stock", 10)
    movement.current_stock = overrides.get("current_stock", 15)
    movement.reason = overrides.get("reason", "Compra de reposição")
    from datetime import UTC, datetime

    movement.created_at = overrides.get("created_at") or datetime.now(UTC)
    return movement


@patch("app.modules.products.use_cases.adjust_product_stock_use_case.record_audit_log", AsyncMock())
async def test_adjust_stock_applies_in_movement() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = AdjustProductStockUseCase(connection_manager=connection_manager)
    product = _build_product_mock(stock=10)

    with (
        patch(
            "app.modules.products.services.stock_movement_service.ProductRepository"
        ) as repo_cls,
        patch(
            "app.modules.products.services.stock_movement_service.StockMovementRepository"
        ) as movement_repo_cls,
    ):
        repo_cls.return_value.get_by_id = AsyncMock(return_value=product)
        repo_cls.return_value.update = AsyncMock()
        movement_repo_cls.return_value.create = AsyncMock(
            side_effect=lambda movement: movement
        )

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            product_id=product.id,
            payload=CreateStockMovementRequest(
                movement="in", quantity=5, reason="Compra de reposição"
            ),
        )

        repo_cls.return_value.update.assert_awaited_once_with(product, {"stock": 15})

    assert result.previous_stock == 10
    assert result.current_stock == 15


@patch("app.modules.products.use_cases.adjust_product_stock_use_case.record_audit_log", AsyncMock())
async def test_adjust_stock_rejects_out_movement_that_goes_negative() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = AdjustProductStockUseCase(connection_manager=connection_manager)
    product = _build_product_mock(stock=2)

    with patch(
        "app.modules.products.services.stock_movement_service.ProductRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=product)

        with pytest.raises(ConflictError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                product_id=product.id,
                payload=CreateStockMovementRequest(
                    movement="out", quantity=5, reason="Venda balcão"
                ),
            )


async def test_adjust_stock_sets_absolute_value_for_adjustment_movement() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = AdjustProductStockUseCase(connection_manager=connection_manager)
    product = _build_product_mock(stock=10)

    with (
        patch(
            "app.modules.products.services.stock_movement_service.ProductRepository"
        ) as repo_cls,
        patch(
            "app.modules.products.services.stock_movement_service.StockMovementRepository"
        ) as movement_repo_cls,
        patch(
            "app.modules.products.use_cases.adjust_product_stock_use_case.record_audit_log",
            AsyncMock(),
        ),
    ):
        repo_cls.return_value.get_by_id = AsyncMock(return_value=product)
        repo_cls.return_value.update = AsyncMock()
        movement_repo_cls.return_value.create = AsyncMock(
            side_effect=lambda movement: movement
        )

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            product_id=product.id,
            payload=CreateStockMovementRequest(
                movement="adjustment", quantity=7, reason="Contagem de inventário"
            ),
        )

        repo_cls.return_value.update.assert_awaited_once_with(product, {"stock": 7})

    assert result.current_stock == 7


async def test_adjust_stock_raises_not_found_for_missing_product() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = AdjustProductStockUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.products.services.stock_movement_service.ProductRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                product_id=uuid.uuid4(),
                payload=CreateStockMovementRequest(
                    movement="in", quantity=5, reason="Compra"
                ),
            )


async def test_list_stock_movements_raises_not_found_for_missing_product() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = ListStockMovementsUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.products.use_cases.list_stock_movements_use_case.ProductRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                product_id=uuid.uuid4(),
                filters=StockMovementFilterParams(),
            )


async def test_list_stock_movements_computes_pagination_meta() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = ListStockMovementsUseCase(connection_manager=connection_manager)
    product = _build_product_mock()
    movement = _build_movement_mock(product_id=product.id)

    with (
        patch(
            "app.modules.products.use_cases.list_stock_movements_use_case.ProductRepository"
        ) as repo_cls,
        patch(
            "app.modules.products.use_cases.list_stock_movements_use_case.StockMovementRepository"
        ) as movement_repo_cls,
    ):
        repo_cls.return_value.get_by_id = AsyncMock(return_value=product)
        movement_repo_cls.return_value.list_by_product = AsyncMock(
            return_value=([movement], 25)
        )

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            product_id=product.id,
            filters=StockMovementFilterParams(page=1, page_size=10),
        )

    assert result.meta.total == 25
    assert result.meta.pages == 3
    assert len(result.items) == 1
