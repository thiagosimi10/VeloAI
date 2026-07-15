import uuid
from contextlib import asynccontextmanager
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from veloai_shared.exceptions import ConflictError, NotFoundError

from app.modules.products.schemas.product import (
    CreateProductRequest,
    ProductFilterParams,
    UpdateProductRequest,
)
from app.modules.products.use_cases.create_product_use_case import CreateProductUseCase
from app.modules.products.use_cases.delete_product_use_case import DeleteProductUseCase
from app.modules.products.use_cases.get_product_use_case import GetProductUseCase
from app.modules.products.use_cases.list_products_use_case import ListProductsUseCase
from app.modules.products.use_cases.update_product_use_case import UpdateProductUseCase


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
    product.category_id = overrides.get("category_id")
    product.supplier_id = overrides.get("supplier_id")
    product.sku = overrides.get("sku", "SSD-KGN-1TB")
    product.barcode = overrides.get("barcode")
    product.name = overrides.get("name", "SSD Kingston 1TB")
    product.description = None
    product.cost_price = overrides.get("cost_price", Decimal("320.00"))
    product.sale_price = overrides.get("sale_price", Decimal("490.00"))
    product.stock = overrides.get("stock", 20)
    product.minimum_stock = None
    product.maximum_stock = None
    product.unit = "UN"
    product.weight = None
    product.active = overrides.get("active", True)
    from datetime import UTC, datetime

    product.created_at = overrides.get("created_at") or datetime.now(UTC)
    product.updated_at = overrides.get("updated_at") or datetime.now(UTC)
    return product


async def test_list_products_computes_pagination_meta() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = ListProductsUseCase(connection_manager=connection_manager)

    product = _build_product_mock()
    with patch(
        "app.modules.products.use_cases.list_products_use_case.ProductRepository"
    ) as repo_cls:
        repo_cls.return_value.list = AsyncMock(return_value=([product], 25))

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            filters=ProductFilterParams(page=1, page_size=10),
        )

    assert result.meta.total == 25
    assert result.meta.pages == 3
    assert len(result.items) == 1
    assert result.items[0].sku == "SSD-KGN-1TB"


async def test_get_product_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = GetProductUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.products.use_cases.get_product_use_case.ProductRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(), database_name="tenant_abc", product_id=uuid.uuid4()
            )


def _create_payload(**overrides: object) -> CreateProductRequest:
    defaults: dict[str, object] = {
        "sku": "SSD-KGN-1TB",
        "name": "SSD Kingston 1TB",
        "cost_price": Decimal("320.00"),
        "sale_price": Decimal("490.00"),
    }
    defaults.update(overrides)
    return CreateProductRequest(**defaults)  # type: ignore[arg-type]


async def test_create_product_rejects_duplicate_sku() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CreateProductUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.products.use_cases.create_product_use_case.ProductRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_sku = AsyncMock(return_value=_build_product_mock())

        with pytest.raises(ConflictError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                payload=_create_payload(),
            )


async def test_create_product_rejects_nonexistent_category() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CreateProductUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.products.use_cases.create_product_use_case.GetCategoryUseCase"
    ) as get_category_cls:
        get_category_cls.return_value.execute = AsyncMock(
            side_effect=NotFoundError("Categoria não encontrada.", code="CATEGORY_NOT_FOUND")
        )

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                payload=_create_payload(category_id=uuid.uuid4()),
            )


async def test_create_product_rejects_nonexistent_supplier() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CreateProductUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.products.use_cases.create_product_use_case.GetSupplierUseCase"
    ) as get_supplier_cls:
        get_supplier_cls.return_value.execute = AsyncMock(
            side_effect=NotFoundError("Fornecedor não encontrado.", code="SUPPLIER_NOT_FOUND")
        )

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                payload=_create_payload(supplier_id=uuid.uuid4()),
            )


async def test_update_product_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = UpdateProductUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.products.use_cases.update_product_use_case.ProductRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                product_id=uuid.uuid4(),
                payload=UpdateProductRequest(name="Novo Nome"),
            )


async def test_update_product_rejects_barcode_already_used_by_another_product() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = UpdateProductUseCase(connection_manager=connection_manager)
    product = _build_product_mock(barcode="789000000001")
    other_product = _build_product_mock(id=uuid.uuid4(), barcode="789000000002")

    with patch(
        "app.modules.products.use_cases.update_product_use_case.ProductRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=product)
        repo_cls.return_value.get_by_barcode = AsyncMock(return_value=other_product)

        with pytest.raises(ConflictError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                product_id=product.id,
                payload=UpdateProductRequest(barcode="789000000002"),
            )


async def test_delete_product_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = DeleteProductUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.products.use_cases.delete_product_use_case.ProductRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                product_id=uuid.uuid4(),
            )
