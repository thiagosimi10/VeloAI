"""Caso de uso: produtos mais vendidos (soma de `sale_items` + `service_order_items`
com `product_id`), para o gráfico de barras do Dashboard."""

from __future__ import annotations

import uuid

from app.core.database import TenantConnectionManager
from app.modules.dashboard.repositories.dashboard_repository import DashboardRepository
from app.modules.dashboard.schemas.dashboard import TopProductItem


class GetTopProductsUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, limit: int
    ) -> list[TopProductItem]:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            rows = await DashboardRepository(session).top_products_by_quantity(limit)

        return [
            TopProductItem(product_id=product_id, name=name, quantity_sold=quantity_sold)
            for product_id, name, quantity_sold in rows
        ]
