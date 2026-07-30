"""Caso de uso: atualizar os dados cadastrais da própria empresa. `legal_name`/
`trade_name` também vivem duplicados no Banco Master (`Tenant`, usado pelo Painel
Administrativo e exibido no cabeçalho do app via `/auth/me`) — sempre sincronizados
juntos aqui, reaproveitando `UpdateTenantUseCase` (já usado pelo admin), para nunca os
dois ficarem divergentes."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.admin.use_cases.update_tenant_use_case import UpdateTenantUseCase
from app.modules.company.repositories.company_repository import CompanyRepository
from app.modules.company.schemas.company import CompanyResponse, UpdateCompanyRequest
from app.modules.company.use_cases._helpers import serialize_company


class UpdateCompanyUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        payload: UpdateCompanyRequest,
    ) -> CompanyResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = CompanyRepository(session)
            company = await repository.get_the_company()
            if company is None:
                raise NotFoundError("Empresa não encontrada.", code="COMPANY_NOT_FOUND")

            before = serialize_company(company)
            update_data = payload.model_dump(exclude_unset=True)
            await repository.update(company, update_data)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="COMPANY_UPDATED",
                resource="company",
                before=before,
                after=serialize_company(company),
            )
            await session.commit()

            response = CompanyResponse.model_validate(company)

        await UpdateTenantUseCase().execute(
            tenant_id=tenant_id,
            legal_name=response.legal_name,
            trade_name=response.trade_name,
        )

        return response
