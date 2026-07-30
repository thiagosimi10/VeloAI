"""Caso de uso: buscar os dados cadastrais da própria empresa."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.database import TenantConnectionManager
from app.modules.company.repositories.company_repository import CompanyRepository
from app.modules.company.schemas.company import CompanyResponse


class GetCompanyUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(self, *, tenant_id: uuid.UUID, database_name: str) -> CompanyResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            company = await CompanyRepository(session).get_the_company()
            if company is None:
                raise NotFoundError("Empresa não encontrada.", code="COMPANY_NOT_FOUND")
            return CompanyResponse.model_validate(company)
