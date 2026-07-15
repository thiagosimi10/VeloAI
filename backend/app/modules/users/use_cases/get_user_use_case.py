"""Caso de uso: buscar um usuário pelo id."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.database import TenantConnectionManager
from app.modules.users.repositories.user_repository import UserRepository
from app.modules.users.schemas.user import UserResponse


class GetUserUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, user_id: uuid.UUID
    ) -> UserResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            user = await UserRepository(session).get_by_id(user_id)
            if user is None:
                raise NotFoundError("Usuário não encontrado.", code="USER_NOT_FOUND")
            return UserResponse.model_validate(user)
