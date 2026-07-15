"""Caso de uso: listar Contas a Pagar com filtros e paginação, conforme
22-API-STANDARDS.md. Ordenado por vencimento (mais próximas primeiro)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from veloai_shared.responses import PaginationMeta

from app.core.database import TenantConnectionManager
from app.modules.finance.repositories.account_payable_repository import (
    AccountPayableRepository,
)
from app.modules.finance.schemas.account_payable import (
    AccountPayableFilterParams,
    AccountPayableResponse,
)


@dataclass(frozen=True)
class ListAccountPayablesResult:
    items: list[AccountPayableResponse]
    meta: PaginationMeta


class ListAccountPayablesUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, filters: AccountPayableFilterParams
    ) -> ListAccountPayablesResult:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            payables, total = await AccountPayableRepository(session).list(filters)

        pages = (total + filters.page_size - 1) // filters.page_size if total else 0
        return ListAccountPayablesResult(
            items=[AccountPayableResponse.model_validate(payable) for payable in payables],
            meta=PaginationMeta(
                page=filters.page, page_size=filters.page_size, total=total, pages=pages
            ),
        )
