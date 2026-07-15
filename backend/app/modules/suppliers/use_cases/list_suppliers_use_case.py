"""Caso de uso: listar fornecedores com busca, ordenação e paginação, conforme
22-API-STANDARDS.md."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from veloai_shared.responses import PaginationMeta

from app.core.database import TenantConnectionManager
from app.modules.suppliers.repositories.supplier_repository import SupplierRepository
from app.modules.suppliers.schemas.supplier import SupplierFilterParams, SupplierResponse


@dataclass(frozen=True)
class ListSuppliersResult:
    items: list[SupplierResponse]
    meta: PaginationMeta


class ListSuppliersUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, filters: SupplierFilterParams
    ) -> ListSuppliersResult:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            suppliers, total = await SupplierRepository(session).list(filters)

        pages = (total + filters.page_size - 1) // filters.page_size if total else 0
        return ListSuppliersResult(
            items=[SupplierResponse.model_validate(supplier) for supplier in suppliers],
            meta=PaginationMeta(
                page=filters.page, page_size=filters.page_size, total=total, pages=pages
            ),
        )
