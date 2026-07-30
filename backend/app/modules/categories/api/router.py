"""Controller do módulo de Categorias. Responsabilidade: receber requisição, validar
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
from app.modules.categories.permissions import (
    CATEGORIES_CREATE,
    CATEGORIES_DELETE,
    CATEGORIES_UPDATE,
    CATEGORIES_VIEW,
)
from app.modules.categories.schemas.category import (
    CategoryFilterParams,
    CategoryResponse,
    CreateCategoryRequest,
    UpdateCategoryRequest,
)
from app.modules.categories.use_cases.create_category_use_case import CreateCategoryUseCase
from app.modules.categories.use_cases.delete_category_use_case import DeleteCategoryUseCase
from app.modules.categories.use_cases.get_category_use_case import GetCategoryUseCase
from app.modules.categories.use_cases.import_categories_use_case import ImportCategoriesUseCase
from app.modules.categories.use_cases.list_categories_use_case import ListCategoriesUseCase
from app.modules.categories.use_cases.update_category_use_case import UpdateCategoryUseCase

router = APIRouter(prefix="/categories", tags=["categories"])

_MAX_IMPORT_FILE_SIZE_BYTES = 5 * 1024 * 1024


@router.get("")
async def list_categories(
    filters: CategoryFilterParams = Depends(),
    current_user: CurrentUser = Depends(require_permission(CATEGORIES_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[CategoryResponse]]:
    use_case = ListCategoriesUseCase(connection_manager=connection_manager)
    result = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        filters=filters,
    )
    return SuccessResponse(
        message="Categorias listadas com sucesso.", data=result.items, meta=result.meta
    )


@router.get("/{category_id}")
async def get_category(
    category_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(CATEGORIES_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[CategoryResponse]:
    use_case = GetCategoryUseCase(connection_manager=connection_manager)
    category = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        category_id=category_id,
    )
    return SuccessResponse(message="Categoria encontrada.", data=category)


@router.post("", status_code=201)
async def create_category(
    payload: CreateCategoryRequest,
    current_user: CurrentUser = Depends(require_permission(CATEGORIES_CREATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[CategoryResponse]:
    use_case = CreateCategoryUseCase(connection_manager=connection_manager)
    category = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        payload=payload,
    )
    return SuccessResponse(message="Categoria criada com sucesso.", data=category)


@router.post("/import")
async def import_categories(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(require_permission(CATEGORIES_CREATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[ImportResultResponse]:
    data = await file.read()
    if len(data) > _MAX_IMPORT_FILE_SIZE_BYTES:
        raise ValidationError(
            "Arquivo muito grande. O limite é 5MB.", code="IMPORT_FILE_TOO_LARGE"
        )

    use_case = ImportCategoriesUseCase(connection_manager=connection_manager)
    result = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        filename=file.filename or "arquivo",
        data=data,
    )
    return SuccessResponse(
        message=f"{result.created} de {result.total_rows} categoria(s) importada(s).",
        data=to_import_result_response(result),
    )


@router.patch("/{category_id}")
async def update_category(
    category_id: uuid.UUID,
    payload: UpdateCategoryRequest,
    current_user: CurrentUser = Depends(require_permission(CATEGORIES_UPDATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[CategoryResponse]:
    use_case = UpdateCategoryUseCase(connection_manager=connection_manager)
    category = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        category_id=category_id,
        payload=payload,
    )
    return SuccessResponse(message="Categoria atualizada com sucesso.", data=category)


@router.delete("/{category_id}")
async def delete_category(
    category_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(CATEGORIES_DELETE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[dict[str, str]]:
    use_case = DeleteCategoryUseCase(connection_manager=connection_manager)
    await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        category_id=category_id,
    )
    return SuccessResponse(message="Categoria excluída com sucesso.", data={})
