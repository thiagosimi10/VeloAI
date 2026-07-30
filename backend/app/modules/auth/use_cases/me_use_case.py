"""Caso de uso: `GET /auth/me`. Retorna o perfil e as permissões do usuário autenticado
a partir das claims já validadas do access token."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from veloai_shared.exceptions import AuthenticationError

from app.core.database import TenantConnectionManager
from app.core.storage import StorageClient
from app.modules.auth.repositories.user_repository import TenantUserRepository
from app.modules.auth.use_cases._helpers import resolve_avatar_url


@dataclass(frozen=True)
class MeResult:
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str | None
    role: str
    permissions: list[str]
    must_change_password: bool
    tenant_name: str
    avatar_url: str | None


class MeUseCase:
    def __init__(
        self, *, connection_manager: TenantConnectionManager, storage_client: StorageClient
    ) -> None:
        self._connections = connection_manager
        self._storage = storage_client

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
            user_id_, email, first_name, last_name, must_change_password, avatar_key = (
                user.id,
                user.email,
                user.first_name,
                user.last_name,
                user.force_password_change,
                user.avatar_key,
            )

        tenant = await self._connections.get_tenant_by_id(tenant_id)
        tenant_name = (tenant.trade_name or tenant.legal_name) if tenant else ""
        avatar_url = await resolve_avatar_url(self._storage, avatar_key)

        return MeResult(
            id=user_id_,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            permissions=permissions,
            must_change_password=must_change_password,
            tenant_name=tenant_name,
            avatar_url=avatar_url,
        )
