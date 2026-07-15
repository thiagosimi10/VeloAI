"""Controller do módulo de Usuários (somente leitura nesta fase). Responsabilidade:
receber requisição, validar permissão via `require_permission` e delegar ao Use Case —
nunca conter regra de negócio (00-AI-CONSTITUTION.md)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from veloai_shared.responses import SuccessResponse

from app.core.database import TenantConnectionManager, get_tenant_connection_manager
from app.core.dependencies import CurrentUser, require_permission
from app.modules.users.permissions import USERS_VIEW
from app.modules.users.schemas.user import UserFilterParams, UserResponse
from app.modules.users.use_cases.get_user_use_case import GetUserUseCase
from app.modules.users.use_cases.list_users_use_case import ListUsersUseCase

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
async def list_users(
    filters: UserFilterParams = Depends(),
    current_user: CurrentUser = Depends(require_permission(USERS_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[UserResponse]]:
    use_case = ListUsersUseCase(connection_manager=connection_manager)
    result = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        filters=filters,
    )
    return SuccessResponse(
        message="Usuários listados com sucesso.", data=result.items, meta=result.meta
    )


@router.get("/{user_id}")
async def get_user(
    user_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(USERS_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[UserResponse]:
    use_case = GetUserUseCase(connection_manager=connection_manager)
    user = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        user_id=user_id,
    )
    return SuccessResponse(message="Usuário encontrado.", data=user)
