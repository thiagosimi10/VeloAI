"""Caso de uso: Troca de Senha. Obrigatória no primeiro login (usuário semeado pelo
Provisioning recebe senha temporária) e disponível a qualquer momento depois, conforme
29-SECURITY.md ("Troca de senha invalida sessões anteriores.")."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import AuthenticationError
from veloai_shared.security import hash_password, verify_password

from app.core.database import TenantConnectionManager
from app.modules.auth.repositories.refresh_token_repository import RefreshTokenRepository
from app.modules.auth.repositories.user_repository import TenantUserRepository


class ChangePasswordUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        user_id: uuid.UUID,
        current_password: str,
        new_password: str,
    ) -> None:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            user_repository = TenantUserRepository(session)
            user = await user_repository.get_by_id(user_id)
            if user is None or not verify_password(current_password, user.password_hash):
                raise AuthenticationError("Senha atual incorreta.", code="INVALID_CREDENTIALS")

            await user_repository.update_password(user, hash_password(new_password))

            refresh_repository = RefreshTokenRepository(session)
            await refresh_repository.revoke_all_for_user(user_id)

            await session.commit()
