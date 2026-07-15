"""Controller do módulo de Vendas. Responsabilidade: receber requisição, validar
permissão via `require_permission` e delegar ao Use Case — nunca conter regra de
negócio (00-AI-CONSTITUTION.md). Sem `DELETE /{sale_id}` — vendas nunca são excluídas,
apenas canceladas (12-VENDAS.md: "Nunca excluir vendas. Sempre cancelar.")."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from veloai_shared.responses import SuccessResponse

from app.core.database import TenantConnectionManager, get_tenant_connection_manager
from app.core.dependencies import CurrentUser, require_permission
from app.modules.sales.permissions import (
    SALES_CANCEL,
    SALES_COMPLETE,
    SALES_CREATE,
    SALES_UPDATE,
    SALES_VIEW,
)
from app.modules.sales.schemas.sale import (
    CreateSaleRequest,
    SaleFilterParams,
    SaleResponse,
    UpdateSaleRequest,
)
from app.modules.sales.schemas.sale_item import AddSaleItemRequest, SaleItemResponse
from app.modules.sales.use_cases.add_sale_item_use_case import AddSaleItemUseCase
from app.modules.sales.use_cases.cancel_sale_use_case import CancelSaleUseCase
from app.modules.sales.use_cases.complete_sale_use_case import CompleteSaleUseCase
from app.modules.sales.use_cases.create_sale_use_case import CreateSaleUseCase
from app.modules.sales.use_cases.get_sale_use_case import GetSaleUseCase
from app.modules.sales.use_cases.list_sales_use_case import ListSalesUseCase
from app.modules.sales.use_cases.remove_sale_item_use_case import RemoveSaleItemUseCase
from app.modules.sales.use_cases.update_sale_use_case import UpdateSaleUseCase

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("")
async def list_sales(
    filters: SaleFilterParams = Depends(),
    current_user: CurrentUser = Depends(require_permission(SALES_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[SaleResponse]]:
    use_case = ListSalesUseCase(connection_manager=connection_manager)
    result = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        filters=filters,
    )
    return SuccessResponse(
        message="Vendas listadas com sucesso.", data=result.items, meta=result.meta
    )


@router.get("/{sale_id}")
async def get_sale(
    sale_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(SALES_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[SaleResponse]:
    use_case = GetSaleUseCase(connection_manager=connection_manager)
    sale = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        sale_id=sale_id,
    )
    return SuccessResponse(message="Venda encontrada.", data=sale)


@router.post("", status_code=201)
async def create_sale(
    payload: CreateSaleRequest,
    current_user: CurrentUser = Depends(require_permission(SALES_CREATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[SaleResponse]:
    use_case = CreateSaleUseCase(connection_manager=connection_manager)
    sale = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        payload=payload,
    )
    return SuccessResponse(message="Venda criada com sucesso.", data=sale)


@router.patch("/{sale_id}")
async def update_sale(
    sale_id: uuid.UUID,
    payload: UpdateSaleRequest,
    current_user: CurrentUser = Depends(require_permission(SALES_UPDATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[SaleResponse]:
    use_case = UpdateSaleUseCase(connection_manager=connection_manager)
    sale = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        sale_id=sale_id,
        payload=payload,
    )
    return SuccessResponse(message="Venda atualizada com sucesso.", data=sale)


@router.post("/{sale_id}/items", status_code=201)
async def add_sale_item(
    sale_id: uuid.UUID,
    payload: AddSaleItemRequest,
    current_user: CurrentUser = Depends(require_permission(SALES_UPDATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[SaleItemResponse]:
    use_case = AddSaleItemUseCase(connection_manager=connection_manager)
    item = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        sale_id=sale_id,
        payload=payload,
    )
    return SuccessResponse(message="Item adicionado com sucesso.", data=item)


@router.delete("/{sale_id}/items/{item_id}")
async def remove_sale_item(
    sale_id: uuid.UUID,
    item_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(SALES_UPDATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[dict[str, str]]:
    use_case = RemoveSaleItemUseCase(connection_manager=connection_manager)
    await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        sale_id=sale_id,
        item_id=item_id,
    )
    return SuccessResponse(message="Item removido com sucesso.", data={})


@router.post("/{sale_id}/complete")
async def complete_sale(
    sale_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(SALES_COMPLETE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[SaleResponse]:
    use_case = CompleteSaleUseCase(connection_manager=connection_manager)
    sale = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        sale_id=sale_id,
    )
    return SuccessResponse(message="Venda concluída com sucesso.", data=sale)


@router.post("/{sale_id}/cancel")
async def cancel_sale(
    sale_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(SALES_CANCEL)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[SaleResponse]:
    use_case = CancelSaleUseCase(connection_manager=connection_manager)
    sale = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        sale_id=sale_id,
    )
    return SuccessResponse(message="Venda cancelada com sucesso.", data=sale)
