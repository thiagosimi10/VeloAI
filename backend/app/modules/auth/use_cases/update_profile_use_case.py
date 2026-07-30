"""Caso de uso: atualizar o próprio perfil (nome). Sempre escopado ao usuário
autenticado — nunca recebe um `user_id` de fora, diferente do módulo `users/`
(gestão de outros usuários, fora do escopo desta fase)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import AuthenticationError

from app.core.database import TenantConnectionManager
from app.modules.auth.repositories.user_repository import TenantUserRepository


class UpdateProfileUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        user_id: uuid.UUID,
        first_name: str,
        last_name: str | None,
    ) -> None:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            user_repository = TenantUserRepository(session)
            user = await user_repository.get_by_id(user_id)
            if user is None:
                raise AuthenticationError("Usuário não encontrado.", code="NOT_AUTHENTICATED")

            await user_repository.update_profile(
                user, first_name=first_name, last_name=last_name
            )
            await session.commit()
