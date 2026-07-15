"""Caso de uso: listar Vendas com filtros e paginação, conforme 22-API-STANDARDS.md. As
linhas da listagem não carregam os itens (só a busca por id faz isso) — evita N+1
consultas para exibir uma tabela."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from veloai_shared.responses import PaginationMeta

from app.core.database import TenantConnectionManager
from app.modules.sales.repositories.sale_repository import SaleRepository
from app.modules.sales.schemas.sale import SaleFilterParams, SaleResponse
from app.modules.sales.use_cases._helpers import to_response


@dataclass(frozen=True)
class ListSalesResult:
    items: list[SaleResponse]
    meta: PaginationMeta


class ListSalesUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, filters: SaleFilterParams
    ) -> ListSalesResult:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            sales, total = await SaleRepository(session).list(filters)

        pages = (total + filters.page_size - 1) // filters.page_size if total else 0
        return ListSalesResult(
            items=[to_response(sale) for sale in sales],
            meta=PaginationMeta(
                page=filters.page, page_size=filters.page_size, total=total, pages=pages
            ),
        )
