"""Caso de uso: quantidade de produtos ativos por categoria, para o gráfico de
Produtos por Categoria do Dashboard."""

from __future__ import annotations

import uuid

from app.core.database import TenantConnectionManager
from app.modules.dashboard.repositories.dashboard_repository import DashboardRepository
from app.modules.dashboard.schemas.dashboard import CategoryProductCount


class GetProductsByCategoryUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str
    ) -> list[CategoryProductCount]:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = DashboardRepository(session)
            rows = await repository.count_products_by_category()

        return [
            CategoryProductCount(category_name=name, product_count=count) for name, count in rows
        ]
