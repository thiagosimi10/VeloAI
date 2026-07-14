"""Controller do Provisioning Service. Responsabilidade: receber requisição, validar e
chamar o Service — nunca conter regra de negócio (00-AI-CONSTITUTION.md)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter
from veloai_shared.exceptions import NotFoundError
from veloai_shared.responses import SuccessResponse

from app.schemas.tenant import CreateTenantRequest, TenantProvisionedResponse, TenantResponse
from app.services.tenant_provisioning_service import TenantProvisioningService

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("", status_code=201)
async def create_tenant(
    payload: CreateTenantRequest,
) -> SuccessResponse[TenantProvisionedResponse]:
    service = TenantProvisioningService()
    result = await service.provision(payload)
    return SuccessResponse(message="Empresa provisionada com sucesso.", data=result)


@router.get("/{tenant_id}")
async def get_tenant(tenant_id: uuid.UUID) -> SuccessResponse[TenantResponse]:
    service = TenantProvisioningService()
    tenant = await service.get(tenant_id)
    if tenant is None:
        raise NotFoundError("Tenant não encontrado.", code="TENANT_NOT_FOUND")

    return SuccessResponse(
        message="Tenant encontrado.",
        data=TenantResponse(
            tenant_id=tenant.id,
            legal_name=tenant.legal_name,
            document=tenant.document,
            database_name=tenant.database_name,
            status=tenant.status,
        ),
    )
