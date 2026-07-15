"""Acesso ao banco do tenant para Produtos. Nenhuma regra de negócio aqui — apenas
persistência e consulta, conforme 00-AI-CONSTITUTION.md."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import Product

from app.modules.products.schemas.product import ProductFilterParams

_SORT_COLUMNS = {
    "name": Product.name,
    "sku": Product.sku,
    "created_at": Product.created_at,
}


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, product_id: uuid.UUID) -> Product | None:
        result = await self._session.execute(
            select(Product).where(Product.id == product_id, Product.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_sku(self, sku: str) -> Product | None:
        result = await self._session.execute(
            select(Product).where(Product.sku == sku, Product.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_barcode(self, barcode: str) -> Product | None:
        result = await self._session.execute(
            select(Product).where(Product.barcode == barcode, Product.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list(self, filters: ProductFilterParams) -> tuple[list[Product], int]:
        conditions = [Product.deleted_at.is_(None)]
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    Product.name.ilike(pattern),
                    Product.sku.ilike(pattern),
                    Product.barcode.ilike(pattern),
                )
            )
        if filters.category_id is not None:
            conditions.append(Product.category_id == filters.category_id)
        if filters.supplier_id is not None:
            conditions.append(Product.supplier_id == filters.supplier_id)

        count_result = await self._session.execute(
            select(func.count()).select_from(Product).where(*conditions)
        )
        total = int(count_result.scalar_one())

        sort_column = _SORT_COLUMNS[filters.sort]
        order_by = sort_column.asc() if filters.order == "asc" else sort_column.desc()

        list_result = await self._session.execute(
            select(Product)
            .where(*conditions)
            .order_by(order_by)
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
        )
        return list(list_result.scalars().all()), total

    async def create(self, product: Product) -> Product:
        self._session.add(product)
        await self._session.flush()
        return product

    async def update(self, product: Product, data: dict[str, Any]) -> Product:
        for field, value in data.items():
            setattr(product, field, value)
        await self._session.flush()
        return product

    async def soft_delete(self, product: Product) -> None:
        product.deleted_at = datetime.now(UTC)
        product.active = False
        await self._session.flush()

    async def commit(self) -> None:
        await self._session.commit()
