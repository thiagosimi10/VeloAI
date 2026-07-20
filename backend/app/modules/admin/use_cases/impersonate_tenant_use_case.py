"""Caso de uso: Platform Admin acessa o sistema de uma empresa como o usuário
Administrador dela ("entrar como"), sem conhecer a senha — usado para suporte. Emite os
mesmos tokens de uma sessão normal de tenant (`auth/use_cases/login_use_case.py`), só
que sem verificar senha; a autorização vem de já ser um Platform Admin autenticado."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from veloai_shared.exceptions import ConflictError, NotFoundError
from veloai_shared.schema.master import TenantStatus

from app.core.config import Settings
from app.core.database import TenantConnectionManager, get_master_session
from app.modules.admin.repositories.admin_repository import AdminRepository
from app.modules.auth.repositories.refresh_token_repository import RefreshTokenRepository
from app.modules.auth.repositories.user_repository import TenantUserRepository
from app.modules.auth.services.token_service import TokenService

_ACCESSIBLE_STATUSES = {TenantStatus.ACTIVE.value, TenantStatus.SUSPENDED.value}


@dataclass(frozen=True)
class ImpersonateTenantResult:
    access_token: str
    refresh_token: str


class ImpersonateTenantUseCase:
    def __init__(
        self,
        *,
        settings: Settings,
        connection_manager: TenantConnectionManager,
        token_service: TokenService,
    ) -> None:
        self._settings = settings
        self._connections = connection_manager
        self._tokens = token_service

    async def execute(self, *, tenant_id: uuid.UUID) -> ImpersonateTenantResult:
        async with get_master_session() as session:
            repository = AdminRepository(session)
            tenant = await repository.get_tenant_by_id(tenant_id)
            if tenant is None:
                raise NotFoundError("Empresa não encontrada.", code="TENANT_NOT_FOUND")
            if tenant.status not in _ACCESSIBLE_STATUSES:
                raise ConflictError(
                    "Empresa não está em um status que permite acesso.",
                    code="TENANT_NOT_ACCESSIBLE",
                )

        async with self._connections.session_for_tenant(
            tenant.id, tenant.database_name
        ) as tenant_session:
            user_repository = TenantUserRepository(tenant_session)
            admin_user = await user_repository.get_first_admin_user()
            if admin_user is None:
                raise NotFoundError(
                    "Nenhum usuário administrador encontrado nesta empresa.",
                    code="TENANT_ADMIN_NOT_FOUND",
                )

            role = await user_repository.get_role_name(admin_user.role_id) or ""

            access_token = self._tokens.issue_access_token(
                user_id=admin_user.id,
                tenant_id=tenant.id,
                database_name=tenant.database_name,
                role=role,
            )
            refresh_token = self._tokens.issue_refresh_token(
                user_id=admin_user.id, tenant_id=tenant.id, database_name=tenant.database_name
            )

            refresh_repository = RefreshTokenRepository(tenant_session)
            await refresh_repository.create(
                user_id=admin_user.id,
                token_hash=self._tokens.hash_refresh_token(refresh_token),
                expires_at=datetime.now(UTC)
                + timedelta(days=self._settings.jwt_refresh_token_expire_days),
                user_agent="platform-admin-impersonation",
                ip=None,
            )
            await tenant_session.commit()

        async with get_master_session() as session:
            repository = AdminRepository(session)
            await repository.add_audit_log(
                tenant_id=tenant.id,
                action="ADMIN_TENANT_IMPERSONATED",
                resource="tenants",
                after={"impersonated_user_id": str(admin_user.id)},
            )
            await repository.commit()

        return ImpersonateTenantResult(access_token=access_token, refresh_token=refresh_token)
