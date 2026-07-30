"""Controller do módulo de Configurações da Empresa. Responsabilidade: receber
requisição, validar permissão via `require_permission` e delegar ao Use Case — nunca
conter regra de negócio (00-AI-CONSTITUTION.md)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from veloai_shared.responses import SuccessResponse

from app.core.database import TenantConnectionManager, get_tenant_connection_manager
from app.core.dependencies import CurrentUser, require_permission
from app.modules.company.permissions import COMPANY_MANAGE
from app.modules.company.schemas.company import CompanyResponse, UpdateCompanyRequest
from app.modules.company.use_cases.get_company_use_case import GetCompanyUseCase
from app.modules.company.use_cases.update_company_use_case import UpdateCompanyUseCase

router = APIRouter(prefix="/company", tags=["company"])


@router.get("")
async def get_company(
    current_user: CurrentUser = Depends(require_permission(COMPANY_MANAGE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[CompanyResponse]:
    use_case = GetCompanyUseCase(connection_manager=connection_manager)
    company = await use_case.execute(
        tenant_id=current_user.tenant_id, database_name=current_user.database_name
    )
    return SuccessResponse(message="Empresa encontrada.", data=company)


@router.patch("")
async def update_company(
    payload: UpdateCompanyRequest,
    current_user: CurrentUser = Depends(require_permission(COMPANY_MANAGE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[CompanyResponse]:
    use_case = UpdateCompanyUseCase(connection_manager=connection_manager)
    company = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        payload=payload,
    )
    return SuccessResponse(message="Empresa atualizada com sucesso.", data=company)
