"""Controller do módulo de Ordens de Serviço. Responsabilidade: receber requisição,
validar permissão via `require_permission` e delegar ao Use Case — nunca conter regra
de negócio (00-AI-CONSTITUTION.md)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from veloai_shared.responses import SuccessResponse

from app.core.database import TenantConnectionManager, get_tenant_connection_manager
from app.core.dependencies import CurrentUser, require_permission
from app.modules.service_orders.permissions import (
    SERVICE_ORDERS_CANCEL,
    SERVICE_ORDERS_CLOSE,
    SERVICE_ORDERS_CREATE,
    SERVICE_ORDERS_DELETE,
    SERVICE_ORDERS_UPDATE,
    SERVICE_ORDERS_VIEW,
)
from app.modules.service_orders.schemas.service_order import (
    CloseServiceOrderRequest,
    CreateServiceOrderRequest,
    ServiceOrderFilterParams,
    ServiceOrderResponse,
    UpdateServiceOrderRequest,
)
from app.modules.service_orders.schemas.service_order_item import (
    AddServiceOrderItemRequest,
    ServiceOrderItemResponse,
)
from app.modules.service_orders.use_cases.add_service_order_item_use_case import (
    AddServiceOrderItemUseCase,
)
from app.modules.service_orders.use_cases.cancel_service_order_use_case import (
    CancelServiceOrderUseCase,
)
from app.modules.service_orders.use_cases.close_service_order_use_case import (
    CloseServiceOrderUseCase,
)
from app.modules.service_orders.use_cases.create_service_order_use_case import (
    CreateServiceOrderUseCase,
)
from app.modules.service_orders.use_cases.delete_service_order_use_case import (
    DeleteServiceOrderUseCase,
)
from app.modules.service_orders.use_cases.get_service_order_use_case import (
    GetServiceOrderUseCase,
)
from app.modules.service_orders.use_cases.list_service_orders_use_case import (
    ListServiceOrdersUseCase,
)
from app.modules.service_orders.use_cases.remove_service_order_item_use_case import (
    RemoveServiceOrderItemUseCase,
)
from app.modules.service_orders.use_cases.start_service_order_use_case import (
    StartServiceOrderUseCase,
)
from app.modules.service_orders.use_cases.update_service_order_use_case import (
    UpdateServiceOrderUseCase,
)

router = APIRouter(prefix="/service-orders", tags=["service_orders"])


@router.get("")
async def list_service_orders(
    filters: ServiceOrderFilterParams = Depends(),
    current_user: CurrentUser = Depends(require_permission(SERVICE_ORDERS_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[ServiceOrderResponse]]:
    use_case = ListServiceOrdersUseCase(connection_manager=connection_manager)
    result = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        filters=filters,
    )
    return SuccessResponse(
        message="Ordens de Serviço listadas com sucesso.", data=result.items, meta=result.meta
    )


@router.get("/{order_id}")
async def get_service_order(
    order_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(SERVICE_ORDERS_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[ServiceOrderResponse]:
    use_case = GetServiceOrderUseCase(connection_manager=connection_manager)
    order = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        order_id=order_id,
    )
    return SuccessResponse(message="Ordem de Serviço encontrada.", data=order)


@router.post("", status_code=201)
async def create_service_order(
    payload: CreateServiceOrderRequest,
    current_user: CurrentUser = Depends(require_permission(SERVICE_ORDERS_CREATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[ServiceOrderResponse]:
    use_case = CreateServiceOrderUseCase(connection_manager=connection_manager)
    order = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        payload=payload,
    )
    return SuccessResponse(message="Ordem de Serviço criada com sucesso.", data=order)


@router.patch("/{order_id}")
async def update_service_order(
    order_id: uuid.UUID,
    payload: UpdateServiceOrderRequest,
    current_user: CurrentUser = Depends(require_permission(SERVICE_ORDERS_UPDATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[ServiceOrderResponse]:
    use_case = UpdateServiceOrderUseCase(connection_manager=connection_manager)
    order = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        order_id=order_id,
        payload=payload,
    )
    return SuccessResponse(message="Ordem de Serviço atualizada com sucesso.", data=order)


@router.delete("/{order_id}")
async def delete_service_order(
    order_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(SERVICE_ORDERS_DELETE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[dict[str, str]]:
    use_case = DeleteServiceOrderUseCase(connection_manager=connection_manager)
    await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        order_id=order_id,
    )
    return SuccessResponse(message="Ordem de Serviço excluída com sucesso.", data={})


@router.post("/{order_id}/items", status_code=201)
async def add_service_order_item(
    order_id: uuid.UUID,
    payload: AddServiceOrderItemRequest,
    current_user: CurrentUser = Depends(require_permission(SERVICE_ORDERS_UPDATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[ServiceOrderItemResponse]:
    use_case = AddServiceOrderItemUseCase(connection_manager=connection_manager)
    item = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        order_id=order_id,
        payload=payload,
    )
    return SuccessResponse(message="Item adicionado com sucesso.", data=item)


@router.delete("/{order_id}/items/{item_id}")
async def remove_service_order_item(
    order_id: uuid.UUID,
    item_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(SERVICE_ORDERS_UPDATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[dict[str, str]]:
    use_case = RemoveServiceOrderItemUseCase(connection_manager=connection_manager)
    await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        order_id=order_id,
        item_id=item_id,
    )
    return SuccessResponse(message="Item removido com sucesso.", data={})


@router.post("/{order_id}/start")
async def start_service_order(
    order_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(SERVICE_ORDERS_UPDATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[ServiceOrderResponse]:
    use_case = StartServiceOrderUseCase(connection_manager=connection_manager)
    order = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        order_id=order_id,
    )
    return SuccessResponse(message="Ordem de Serviço iniciada com sucesso.", data=order)


@router.post("/{order_id}/close")
async def close_service_order(
    order_id: uuid.UUID,
    payload: CloseServiceOrderRequest = CloseServiceOrderRequest(),
    current_user: CurrentUser = Depends(require_permission(SERVICE_ORDERS_CLOSE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[ServiceOrderResponse]:
    use_case = CloseServiceOrderUseCase(connection_manager=connection_manager)
    order = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        order_id=order_id,
        payload=payload,
    )
    return SuccessResponse(message="Ordem de Serviço concluída com sucesso.", data=order)


@router.post("/{order_id}/cancel")
async def cancel_service_order(
    order_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(SERVICE_ORDERS_CANCEL)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[ServiceOrderResponse]:
    use_case = CancelServiceOrderUseCase(connection_manager=connection_manager)
    order = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        order_id=order_id,
    )
    return SuccessResponse(message="Ordem de Serviço cancelada com sucesso.", data=order)
