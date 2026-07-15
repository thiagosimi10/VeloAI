"""Caso de uso: listar lançamentos de Fluxo de Caixa com filtro por tipo e paginação,
conforme 22-API-STANDARDS.md."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from veloai_shared.responses import PaginationMeta

from app.core.database import TenantConnectionManager
from app.modules.finance.repositories.cash_flow_repository import CashFlowRepository
from app.modules.finance.schemas.cash_flow import CashFlowEntryResponse, CashFlowFilterParams


@dataclass(frozen=True)
class ListCashFlowEntriesResult:
    items: list[CashFlowEntryResponse]
    meta: PaginationMeta


class ListCashFlowEntriesUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, filters: CashFlowFilterParams
    ) -> ListCashFlowEntriesResult:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            entries, total = await CashFlowRepository(session).list(filters)

        pages = (total + filters.page_size - 1) // filters.page_size if total else 0
        return ListCashFlowEntriesResult(
            items=[CashFlowEntryResponse.model_validate(entry) for entry in entries],
            meta=PaginationMeta(
                page=filters.page, page_size=filters.page_size, total=total, pages=pages
            ),
        )
