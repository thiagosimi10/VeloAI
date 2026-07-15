"""Caso de uso: listar clientes com busca, ordenação e paginação, conforme
22-API-STANDARDS.md."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from veloai_shared.responses import PaginationMeta

from app.core.database import TenantConnectionManager
from app.modules.customers.repositories.customer_repository import CustomerRepository
from app.modules.customers.schemas.customer import CustomerFilterParams, CustomerResponse


@dataclass(frozen=True)
class ListCustomersResult:
    items: list[CustomerResponse]
    meta: PaginationMeta


class ListCustomersUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, filters: CustomerFilterParams
    ) -> ListCustomersResult:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            customers, total = await CustomerRepository(session).list(filters)

        pages = (total + filters.page_size - 1) // filters.page_size if total else 0
        return ListCustomersResult(
            items=[CustomerResponse.model_validate(customer) for customer in customers],
            meta=PaginationMeta(
                page=filters.page, page_size=filters.page_size, total=total, pages=pages
            ),
        )
