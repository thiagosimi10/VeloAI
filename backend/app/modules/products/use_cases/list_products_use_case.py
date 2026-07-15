"""Caso de uso: listar produtos com busca, filtro por categoria/fornecedor, ordenação e
paginação, conforme 22-API-STANDARDS.md."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from veloai_shared.responses import PaginationMeta

from app.core.database import TenantConnectionManager
from app.modules.products.repositories.product_repository import ProductRepository
from app.modules.products.schemas.product import ProductFilterParams, ProductResponse


@dataclass(frozen=True)
class ListProductsResult:
    items: list[ProductResponse]
    meta: PaginationMeta


class ListProductsUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, filters: ProductFilterParams
    ) -> ListProductsResult:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            products, total = await ProductRepository(session).list(filters)

        pages = (total + filters.page_size - 1) // filters.page_size if total else 0
        return ListProductsResult(
            items=[ProductResponse.model_validate(product) for product in products],
            meta=PaginationMeta(
                page=filters.page, page_size=filters.page_size, total=total, pages=pages
            ),
        )
