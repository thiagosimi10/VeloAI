"""Caso de uso: listar Ordens de Serviço com busca, filtros e paginação, conforme
22-API-STANDARDS.md. As linhas da listagem não carregam os itens (só a busca por id
faz isso) — evita N+1 consultas para exibir uma tabela."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from veloai_shared.responses import PaginationMeta

from app.core.database import TenantConnectionManager
from app.modules.service_orders.repositories.service_order_repository import (
    ServiceOrderRepository,
)
from app.modules.service_orders.schemas.service_order import (
    ServiceOrderFilterParams,
    ServiceOrderResponse,
)
from app.modules.service_orders.use_cases._helpers import to_response


@dataclass(frozen=True)
class ListServiceOrdersResult:
    items: list[ServiceOrderResponse]
    meta: PaginationMeta


class ListServiceOrdersUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, filters: ServiceOrderFilterParams
    ) -> ListServiceOrdersResult:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            orders, total = await ServiceOrderRepository(session).list(filters)

        pages = (total + filters.page_size - 1) // filters.page_size if total else 0
        return ListServiceOrdersResult(
            items=[to_response(order) for order in orders],
            meta=PaginationMeta(
                page=filters.page, page_size=filters.page_size, total=total, pages=pages
            ),
        )
