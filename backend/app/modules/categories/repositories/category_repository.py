"""Acesso ao banco do tenant para Categorias. Nenhuma regra de negócio aqui — apenas
persistência e consulta, conforme 00-AI-CONSTITUTION.md."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import Category

from app.modules.categories.schemas.category import CategoryFilterParams


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, category_id: uuid.UUID) -> Category | None:
        result = await self._session.execute(
            select(Category).where(Category.id == category_id, Category.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Category | None:
        result = await self._session.execute(
            select(Category).where(Category.name == name, Category.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Category]:
        """Todas as categorias ativas, sem paginação — usado pela importação em lote de
        produtos para resolver nome → id de uma vez (`import_products_use_case.py`),
        em vez de uma query por linha da planilha."""

        result = await self._session.execute(
            select(Category).where(Category.deleted_at.is_(None))
        )
        return list(result.scalars().all())

    async def list(self, filters: CategoryFilterParams) -> tuple[list[Category], int]:
        conditions = [Category.deleted_at.is_(None)]
        if filters.search:
            conditions.append(Category.name.ilike(f"%{filters.search}%"))

        count_result = await self._session.execute(
            select(func.count()).select_from(Category).where(*conditions)
        )
        total = int(count_result.scalar_one())

        list_result = await self._session.execute(
            select(Category)
            .where(*conditions)
            .order_by(Category.name.asc())
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
        )
        return list(list_result.scalars().all()), total

    async def create(self, category: Category) -> Category:
        self._session.add(category)
        await self._session.flush()
        return category

    async def update(self, category: Category, data: dict[str, Any]) -> Category:
        for field, value in data.items():
            setattr(category, field, value)
        await self._session.flush()
        return category

    async def soft_delete(self, category: Category) -> None:
        category.deleted_at = datetime.now(UTC)
        await self._session.flush()

    async def commit(self) -> None:
        await self._session.commit()
