"""Caso de uso: `GET /auth/me`. Retorna o perfil e as permissões do usuário autenticado
a partir das claims já validadas do access token."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from veloai_shared.exceptions import AuthenticationError

from app.core.database import TenantConnectionManager
from app.modules.auth.repositories.user_repository import TenantUserRepository


@dataclass(frozen=True)
class MeResult:
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str | None
    role: str
    permissions: list[str]
    must_change_password: bool


class MeUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, user_id: uuid.UUID
    ) -> MeResult:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            user_repository = TenantUserRepository(session)
            user = await user_repository.get_by_id(user_id)
            if user is None or not user.active:
                raise AuthenticationError("Usuário inativo ou não encontrado.")

            role = await user_repository.get_role_name(user.role_id) or ""
            permissions = await user_repository.get_role_permissions(user.role_id)

            return MeResult(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=role,
                permissions=permissions,
                must_change_password=user.force_password_change,
            )
