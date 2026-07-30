"""Controller do módulo de Produtos. Responsabilidade: receber requisição, validar
permissão via `require_permission` e delegar ao Use Case — nunca conter regra de
negócio (00-AI-CONSTITUTION.md)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from veloai_shared.exceptions import ValidationError
from veloai_shared.responses import SuccessResponse

from app.core.database import TenantConnectionManager, get_tenant_connection_manager
from app.core.dependencies import CurrentUser, require_permission
from app.core.import_result import ImportResultResponse, to_import_result_response
from app.modules.products.permissions import (
    PRODUCTS_CREATE,
    PRODUCTS_DELETE,
    PRODUCTS_UPDATE,
    PRODUCTS_VIEW,
    STOCK_ADJUST,
    STOCK_VIEW,
)
from app.modules.products.schemas.product import (
    CreateProductRequest,
    ProductFilterParams,
    ProductResponse,
    UpdateProductRequest,
)
from app.modules.products.schemas.stock_movement import (
    CreateStockMovementRequest,
    StockMovementFilterParams,
    StockMovementResponse,
)
from app.modules.products.use_cases.adjust_product_stock_use_case import (
    AdjustProductStockUseCase,
)
from app.modules.products.use_cases.create_product_use_case import CreateProductUseCase
from app.modules.products.use_cases.delete_product_use_case import DeleteProductUseCase
from app.modules.products.use_cases.get_product_use_case import GetProductUseCase
from app.modules.products.use_cases.import_products_use_case import ImportProductsUseCase
from app.modules.products.use_cases.list_products_use_case import ListProductsUseCase
from app.modules.products.use_cases.list_stock_movements_use_case import (
    ListStockMovementsUseCase,
)
from app.modules.products.use_cases.update_product_use_case import UpdateProductUseCase

router = APIRouter(prefix="/products", tags=["products"])

_MAX_IMPORT_FILE_SIZE_BYTES = 5 * 1024 * 1024


@router.get("")
async def list_products(
    filters: ProductFilterParams = Depends(),
    current_user: CurrentUser = Depends(require_permission(PRODUCTS_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[ProductResponse]]:
    use_case = ListProductsUseCase(connection_manager=connection_manager)
    result = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        filters=filters,
    )
    return SuccessResponse(
        message="Produtos listados com sucesso.", data=result.items, meta=result.meta
    )


@router.get("/{product_id}")
async def get_product(
    product_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(PRODUCTS_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[ProductResponse]:
    use_case = GetProductUseCase(connection_manager=connection_manager)
    product = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        product_id=product_id,
    )
    return SuccessResponse(message="Produto encontrado.", data=product)


@router.post("", status_code=201)
async def create_product(
    payload: CreateProductRequest,
    current_user: CurrentUser = Depends(require_permission(PRODUCTS_CREATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[ProductResponse]:
    use_case = CreateProductUseCase(connection_manager=connection_manager)
    product = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        payload=payload,
    )
    return SuccessResponse(message="Produto criado com sucesso.", data=product)


@router.post("/import")
async def import_products(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(require_permission(PRODUCTS_CREATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[ImportResultResponse]:
    data = await file.read()
    if len(data) > _MAX_IMPORT_FILE_SIZE_BYTES:
        raise ValidationError(
            "Arquivo muito grande. O limite é 5MB.", code="IMPORT_FILE_TOO_LARGE"
        )

    use_case = ImportProductsUseCase(connection_manager=connection_manager)
    result = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        filename=file.filename or "arquivo",
        data=data,
    )
    return SuccessResponse(
        message=f"{result.created} de {result.total_rows} produto(s) importado(s).",
        data=to_import_result_response(result),
    )


@router.patch("/{product_id}")
async def update_product(
    product_id: uuid.UUID,
    payload: UpdateProductRequest,
    current_user: CurrentUser = Depends(require_permission(PRODUCTS_UPDATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[ProductResponse]:
    use_case = UpdateProductUseCase(connection_manager=connection_manager)
    product = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        product_id=product_id,
        payload=payload,
    )
    return SuccessResponse(message="Produto atualizado com sucesso.", data=product)


@router.delete("/{product_id}")
async def delete_product(
    product_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(PRODUCTS_DELETE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[dict[str, str]]:
    use_case = DeleteProductUseCase(connection_manager=connection_manager)
    await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        product_id=product_id,
    )
    return SuccessResponse(message="Produto excluído com sucesso.", data={})


@router.get("/{product_id}/stock-movements")
async def list_stock_movements(
    product_id: uuid.UUID,
    filters: StockMovementFilterParams = Depends(),
    current_user: CurrentUser = Depends(require_permission(STOCK_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[StockMovementResponse]]:
    use_case = ListStockMovementsUseCase(connection_manager=connection_manager)
    result = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        product_id=product_id,
        filters=filters,
    )
    return SuccessResponse(
        message="Movimentações de estoque listadas com sucesso.",
        data=result.items,
        meta=result.meta,
    )


@router.post("/{product_id}/stock-movements", status_code=201)
async def create_stock_movement(
    product_id: uuid.UUID,
    payload: CreateStockMovementRequest,
    current_user: CurrentUser = Depends(require_permission(STOCK_ADJUST)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[StockMovementResponse]:
    use_case = AdjustProductStockUseCase(connection_manager=connection_manager)
    movement = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        product_id=product_id,
        payload=payload,
    )
    return SuccessResponse(message="Movimentação de estoque registrada com sucesso.", data=movement)
