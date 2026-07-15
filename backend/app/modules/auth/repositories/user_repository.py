"""Acesso ao usuário do tenant. Nenhuma regra de negócio aqui — apenas persistência e
consulta, conforme 00-AI-CONSTITUTION.md ("Repositories: Nunca validar regras.")."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import (
    TenantPermission,
    TenantRole,
    TenantRolePermission,
    TenantUser,
)


class TenantUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> TenantUser | None:
        result = await self._session.execute(select(TenantUser).where(TenantUser.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> TenantUser | None:
        return await self._session.get(TenantUser, user_id)

    async def get_role_name(self, role_id: uuid.UUID) -> str | None:
        result = await self._session.execute(
            select(TenantRole.name).where(TenantRole.id == role_id)
        )
        return result.scalar_one_or_none()

    async def get_role_permissions(self, role_id: uuid.UUID) -> list[str]:
        result = await self._session.execute(
            select(TenantPermission.module, TenantPermission.action)
            .join(TenantRolePermission, TenantRolePermission.permission_id == TenantPermission.id)
            .where(TenantRolePermission.role_id == role_id)
        )
        return [f"{module}.{action}" for module, action in result.all()]

    async def get_role_permissions_by_name(self, role_name: str) -> list[str]:
        """Usada pelo `require_permission` (RBAC): o access token só embute o nome do
        papel (não o id), então a checagem de permissão parte do nome diretamente."""

        result = await self._session.execute(
            select(TenantPermission.module, TenantPermission.action)
            .join(TenantRolePermission, TenantRolePermission.permission_id == TenantPermission.id)
            .join(TenantRole, TenantRole.id == TenantRolePermission.role_id)
            .where(TenantRole.name == role_name)
        )
        return [f"{module}.{action}" for module, action in result.all()]

    async def update_password(self, user: TenantUser, password_hash: str) -> None:
        user.password_hash = password_hash
        user.force_password_change = False
        await self._session.flush()

    async def touch_last_login(self, user: TenantUser) -> None:
        user.last_login_at = datetime.now(UTC)
        await self._session.flush()

    async def commit(self) -> None:
        await self._session.commit()
