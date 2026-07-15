"""Caso de uso: listar Contas a Receber com filtros e paginação, conforme
22-API-STANDARDS.md. Ordenado por vencimento (mais próximas primeiro)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from veloai_shared.responses import PaginationMeta

from app.core.database import TenantConnectionManager
from app.modules.finance.repositories.account_receivable_repository import (
    AccountReceivableRepository,
)
from app.modules.finance.schemas.account_receivable import (
    AccountReceivableFilterParams,
    AccountReceivableResponse,
)


@dataclass(frozen=True)
class ListAccountReceivablesResult:
    items: list[AccountReceivableResponse]
    meta: PaginationMeta


class ListAccountReceivablesUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        filters: AccountReceivableFilterParams,
    ) -> ListAccountReceivablesResult:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            receivables, total = await AccountReceivableRepository(session).list(filters)

        pages = (total + filters.page_size - 1) // filters.page_size if total else 0
        return ListAccountReceivablesResult(
            items=[
                AccountReceivableResponse.model_validate(receivable)
                for receivable in receivables
            ],
            meta=PaginationMeta(
                page=filters.page, page_size=filters.page_size, total=total, pages=pages
            ),
        )
