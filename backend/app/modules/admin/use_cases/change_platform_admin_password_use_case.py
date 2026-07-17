"""Caso de uso: troca de senha do Platform Admin. Obrigatória no primeiro login (o
admin semeado por `scripts/seed_master.py` recebe `force_password_change=True`),
mesmo espírito de `auth/use_cases/change_password_use_case.py` — sem refresh token
para revogar aqui, já que a sessão de admin é só um access token de curta duração."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import AuthenticationError
from veloai_shared.security import hash_password, verify_password

from app.core.database import get_master_session
from app.modules.admin.repositories.admin_repository import AdminRepository


class ChangePlatformAdminPasswordUseCase:
    async def execute(
        self, *, admin_id: uuid.UUID, current_password: str, new_password: str
    ) -> None:
        async with get_master_session() as session:
            repository = AdminRepository(session)
            admin = await repository.get_platform_admin_by_id(admin_id)
            if admin is None or not verify_password(current_password, admin.password_hash):
                raise AuthenticationError("Senha atual incorreta.", code="INVALID_CREDENTIALS")

            await repository.update_password(admin, hash_password(new_password))
            await repository.commit()
