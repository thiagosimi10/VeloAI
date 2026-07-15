"""Controller do módulo de Fornecedores. Responsabilidade: receber requisição, validar
permissão via `require_permission` e delegar ao Use Case — nunca conter regra de
negócio (00-AI-CONSTITUTION.md)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from veloai_shared.responses import SuccessResponse

from app.core.database import TenantConnectionManager, get_tenant_connection_manager
from app.core.dependencies import CurrentUser, require_permission
from app.modules.suppliers.permissions import (
    SUPPLIERS_CREATE,
    SUPPLIERS_DELETE,
    SUPPLIERS_UPDATE,
    SUPPLIERS_VIEW,
)
from app.modules.suppliers.schemas.supplier import (
    CreateSupplierRequest,
    SupplierFilterParams,
    SupplierResponse,
    UpdateSupplierRequest,
)
from app.modules.suppliers.use_cases.create_supplier_use_case import CreateSupplierUseCase
from app.modules.suppliers.use_cases.delete_supplier_use_case import DeleteSupplierUseCase
from app.modules.suppliers.use_cases.get_supplier_use_case import GetSupplierUseCase
from app.modules.suppliers.use_cases.list_suppliers_use_case import ListSuppliersUseCase
from app.modules.suppliers.use_cases.update_supplier_use_case import UpdateSupplierUseCase

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("")
async def list_suppliers(
    filters: SupplierFilterParams = Depends(),
    current_user: CurrentUser = Depends(require_permission(SUPPLIERS_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[SupplierResponse]]:
    use_case = ListSuppliersUseCase(connection_manager=connection_manager)
    result = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        filters=filters,
    )
    return SuccessResponse(
        message="Fornecedores listados com sucesso.", data=result.items, meta=result.meta
    )


@router.get("/{supplier_id}")
async def get_supplier(
    supplier_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(SUPPLIERS_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[SupplierResponse]:
    use_case = GetSupplierUseCase(connection_manager=connection_manager)
    supplier = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        supplier_id=supplier_id,
    )
    return SuccessResponse(message="Fornecedor encontrado.", data=supplier)


@router.post("", status_code=201)
async def create_supplier(
    payload: CreateSupplierRequest,
    current_user: CurrentUser = Depends(require_permission(SUPPLIERS_CREATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[SupplierResponse]:
    use_case = CreateSupplierUseCase(connection_manager=connection_manager)
    supplier = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        payload=payload,
    )
    return SuccessResponse(message="Fornecedor criado com sucesso.", data=supplier)


@router.patch("/{supplier_id}")
async def update_supplier(
    supplier_id: uuid.UUID,
    payload: UpdateSupplierRequest,
    current_user: CurrentUser = Depends(require_permission(SUPPLIERS_UPDATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[SupplierResponse]:
    use_case = UpdateSupplierUseCase(connection_manager=connection_manager)
    supplier = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        supplier_id=supplier_id,
        payload=payload,
    )
    return SuccessResponse(message="Fornecedor atualizado com sucesso.", data=supplier)


@router.delete("/{supplier_id}")
async def delete_supplier(
    supplier_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(SUPPLIERS_DELETE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[dict[str, str]]:
    use_case = DeleteSupplierUseCase(connection_manager=connection_manager)
    await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        supplier_id=supplier_id,
    )
    return SuccessResponse(message="Fornecedor excluído com sucesso.", data={})
