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

    async def get_first_admin_user(self) -> TenantUser | None:
        """Usuário a ser assumido em uma impersonação de Platform Admin (Painel
        Administrativo, Fase 18) — o papel "Administrador" é criado uma única vez, no
        seed inicial do tenant (`provisioning/app/services/seed_service.py`)."""

        result = await self._session.execute(
            select(TenantUser)
            .join(TenantRole, TenantRole.id == TenantUser.role_id)
            .where(TenantRole.name == "Administrador", TenantUser.active.is_(True))
            .order_by(TenantUser.created_at)
            .limit(1)
        )
        return result.scalars().first()

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

    async def update_profile(
        self, user: TenantUser, *, first_name: str, last_name: str | None
    ) -> None:
        user.first_name = first_name
        user.last_name = last_name
        await self._session.flush()

    async def update_avatar(self, user: TenantUser, avatar_key: str | None) -> None:
        user.avatar_key = avatar_key
        await self._session.flush()

    async def touch_last_login(self, user: TenantUser) -> None:
        user.last_login_at = datetime.now(UTC)
        await self._session.flush()

    async def commit(self) -> None:
        await self._session.commit()
