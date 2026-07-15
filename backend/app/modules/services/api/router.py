"""Controller do módulo de Serviços. Responsabilidade: receber requisição, validar
permissão via `require_permission` e delegar ao Use Case — nunca conter regra de
negócio (00-AI-CONSTITUTION.md)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from veloai_shared.responses import SuccessResponse

from app.core.database import TenantConnectionManager, get_tenant_connection_manager
from app.core.dependencies import CurrentUser, require_permission
from app.modules.services.permissions import (
    SERVICES_CREATE,
    SERVICES_DELETE,
    SERVICES_UPDATE,
    SERVICES_VIEW,
)
from app.modules.services.schemas.service import (
    CreateServiceRequest,
    ServiceFilterParams,
    ServiceResponse,
    UpdateServiceRequest,
)
from app.modules.services.use_cases.create_service_use_case import CreateServiceUseCase
from app.modules.services.use_cases.delete_service_use_case import DeleteServiceUseCase
from app.modules.services.use_cases.get_service_use_case import GetServiceUseCase
from app.modules.services.use_cases.list_services_use_case import ListServicesUseCase
from app.modules.services.use_cases.update_service_use_case import UpdateServiceUseCase

router = APIRouter(prefix="/services", tags=["services"])


@router.get("")
async def list_services(
    filters: ServiceFilterParams = Depends(),
    current_user: CurrentUser = Depends(require_permission(SERVICES_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[ServiceResponse]]:
    use_case = ListServicesUseCase(connection_manager=connection_manager)
    result = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        filters=filters,
    )
    return SuccessResponse(
        message="Serviços listados com sucesso.", data=result.items, meta=result.meta
    )


@router.get("/{service_id}")
async def get_service(
    service_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(SERVICES_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[ServiceResponse]:
    use_case = GetServiceUseCase(connection_manager=connection_manager)
    service = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        service_id=service_id,
    )
    return SuccessResponse(message="Serviço encontrado.", data=service)


@router.post("", status_code=201)
async def create_service(
    payload: CreateServiceRequest,
    current_user: CurrentUser = Depends(require_permission(SERVICES_CREATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[ServiceResponse]:
    use_case = CreateServiceUseCase(connection_manager=connection_manager)
    service = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        payload=payload,
    )
    return SuccessResponse(message="Serviço criado com sucesso.", data=service)


@router.patch("/{service_id}")
async def update_service(
    service_id: uuid.UUID,
    payload: UpdateServiceRequest,
    current_user: CurrentUser = Depends(require_permission(SERVICES_UPDATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[ServiceResponse]:
    use_case = UpdateServiceUseCase(connection_manager=connection_manager)
    service = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        service_id=service_id,
        payload=payload,
    )
    return SuccessResponse(message="Serviço atualizado com sucesso.", data=service)


@router.delete("/{service_id}")
async def delete_service(
    service_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(SERVICES_DELETE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[dict[str, str]]:
    use_case = DeleteServiceUseCase(connection_manager=connection_manager)
    await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        service_id=service_id,
    )
    return SuccessResponse(message="Serviço excluído com sucesso.", data={})
