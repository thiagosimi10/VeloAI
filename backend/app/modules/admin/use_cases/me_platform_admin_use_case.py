"""Caso de uso: `GET /admin/auth/me`. Retorna o perfil do Platform Admin autenticado a
partir das claims já validadas do token."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from veloai_shared.exceptions import AuthenticationError

from app.core.database import get_master_session
from app.modules.admin.repositories.admin_repository import AdminRepository


@dataclass(frozen=True)
class PlatformAdminProfile:
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str | None
    must_change_password: bool


class MePlatformAdminUseCase:
    async def execute(self, *, admin_id: uuid.UUID) -> PlatformAdminProfile:
        async with get_master_session() as session:
            repository = AdminRepository(session)
            admin = await repository.get_platform_admin_by_id(admin_id)
            if admin is None or not admin.active:
                raise AuthenticationError("Operador inativo ou não encontrado.")

            return PlatformAdminProfile(
                id=admin.id,
                email=admin.email,
                first_name=admin.first_name,
                last_name=admin.last_name,
                must_change_password=admin.force_password_change,
            )
