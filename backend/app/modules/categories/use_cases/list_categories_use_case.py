"""Caso de uso: listar categorias com busca e paginação, conforme
22-API-STANDARDS.md."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from veloai_shared.responses import PaginationMeta

from app.core.database import TenantConnectionManager
from app.modules.categories.repositories.category_repository import CategoryRepository
from app.modules.categories.schemas.category import CategoryFilterParams, CategoryResponse


@dataclass(frozen=True)
class ListCategoriesResult:
    items: list[CategoryResponse]
    meta: PaginationMeta


class ListCategoriesUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, filters: CategoryFilterParams
    ) -> ListCategoriesResult:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            categories, total = await CategoryRepository(session).list(filters)

        pages = (total + filters.page_size - 1) // filters.page_size if total else 0
        return ListCategoriesResult(
            items=[CategoryResponse.model_validate(category) for category in categories],
            meta=PaginationMeta(
                page=filters.page, page_size=filters.page_size, total=total, pages=pages
            ),
        )
