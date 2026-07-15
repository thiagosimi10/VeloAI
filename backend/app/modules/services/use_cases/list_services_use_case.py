"""Caso de uso: listar serviços com busca, filtro por categoria, ordenação e paginação,
conforme 22-API-STANDARDS.md."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from veloai_shared.responses import PaginationMeta

from app.core.database import TenantConnectionManager
from app.modules.services.repositories.service_repository import ServiceRepository
from app.modules.services.schemas.service import ServiceFilterParams, ServiceResponse


@dataclass(frozen=True)
class ListServicesResult:
    items: list[ServiceResponse]
    meta: PaginationMeta


class ListServicesUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, filters: ServiceFilterParams
    ) -> ListServicesResult:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            services, total = await ServiceRepository(session).list(filters)

        pages = (total + filters.page_size - 1) // filters.page_size if total else 0
        return ListServicesResult(
            items=[ServiceResponse.model_validate(service) for service in services],
            meta=PaginationMeta(
                page=filters.page, page_size=filters.page_size, total=total, pages=pages
            ),
        )
