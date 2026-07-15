"""Caso de uso: listar o histórico de movimentações de estoque de um produto, conforme
22-API-STANDARDS.md."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from veloai_shared.exceptions import NotFoundError
from veloai_shared.responses import PaginationMeta

from app.core.database import TenantConnectionManager
from app.modules.products.repositories.product_repository import ProductRepository
from app.modules.products.repositories.stock_movement_repository import (
    StockMovementRepository,
)
from app.modules.products.schemas.stock_movement import (
    StockMovementFilterParams,
    StockMovementResponse,
)


@dataclass(frozen=True)
class ListStockMovementsResult:
    items: list[StockMovementResponse]
    meta: PaginationMeta


class ListStockMovementsUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        product_id: uuid.UUID,
        filters: StockMovementFilterParams,
    ) -> ListStockMovementsResult:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            product = await ProductRepository(session).get_by_id(product_id)
            if product is None:
                raise NotFoundError("Produto não encontrado.", code="PRODUCT_NOT_FOUND")

            movements, total = await StockMovementRepository(session).list_by_product(
                product_id, filters
            )

        pages = (total + filters.page_size - 1) // filters.page_size if total else 0
        return ListStockMovementsResult(
            items=[StockMovementResponse.model_validate(movement) for movement in movements],
            meta=PaginationMeta(
                page=filters.page, page_size=filters.page_size, total=total, pages=pages
            ),
        )
