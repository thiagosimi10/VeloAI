"""Controller do módulo de Clientes. Responsabilidade: receber requisição, validar
permissão via `require_permission` e delegar ao Use Case — nunca conter regra de
negócio (00-AI-CONSTITUTION.md)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from veloai_shared.responses import SuccessResponse

from app.core.database import TenantConnectionManager, get_tenant_connection_manager
from app.core.dependencies import CurrentUser, require_permission
from app.modules.customers.permissions import (
    CUSTOMERS_CREATE,
    CUSTOMERS_DELETE,
    CUSTOMERS_UPDATE,
    CUSTOMERS_VIEW,
)
from app.modules.customers.schemas.customer import (
    CreateCustomerRequest,
    CustomerFilterParams,
    CustomerResponse,
    UpdateCustomerRequest,
)
from app.modules.customers.use_cases.create_customer_use_case import CreateCustomerUseCase
from app.modules.customers.use_cases.delete_customer_use_case import DeleteCustomerUseCase
from app.modules.customers.use_cases.get_customer_use_case import GetCustomerUseCase
from app.modules.customers.use_cases.list_customers_use_case import ListCustomersUseCase
from app.modules.customers.use_cases.update_customer_use_case import UpdateCustomerUseCase

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("")
async def list_customers(
    filters: CustomerFilterParams = Depends(),
    current_user: CurrentUser = Depends(require_permission(CUSTOMERS_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[CustomerResponse]]:
    use_case = ListCustomersUseCase(connection_manager=connection_manager)
    result = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        filters=filters,
    )
    return SuccessResponse(
        message="Clientes listados com sucesso.", data=result.items, meta=result.meta
    )


@router.get("/{customer_id}")
async def get_customer(
    customer_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(CUSTOMERS_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[CustomerResponse]:
    use_case = GetCustomerUseCase(connection_manager=connection_manager)
    customer = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        customer_id=customer_id,
    )
    return SuccessResponse(message="Cliente encontrado.", data=customer)


@router.post("", status_code=201)
async def create_customer(
    payload: CreateCustomerRequest,
    current_user: CurrentUser = Depends(require_permission(CUSTOMERS_CREATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[CustomerResponse]:
    use_case = CreateCustomerUseCase(connection_manager=connection_manager)
    customer = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        payload=payload,
    )
    return SuccessResponse(message="Cliente criado com sucesso.", data=customer)


@router.patch("/{customer_id}")
async def update_customer(
    customer_id: uuid.UUID,
    payload: UpdateCustomerRequest,
    current_user: CurrentUser = Depends(require_permission(CUSTOMERS_UPDATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[CustomerResponse]:
    use_case = UpdateCustomerUseCase(connection_manager=connection_manager)
    customer = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        customer_id=customer_id,
        payload=payload,
    )
    return SuccessResponse(message="Cliente atualizado com sucesso.", data=customer)


@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(CUSTOMERS_DELETE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[dict[str, str]]:
    use_case = DeleteCustomerUseCase(connection_manager=connection_manager)
    await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        customer_id=customer_id,
    )
    return SuccessResponse(message="Cliente excluído com sucesso.", data={})
