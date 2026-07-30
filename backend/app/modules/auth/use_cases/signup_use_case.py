"""Caso de uso: cadastro self-service. Provisiona um novo tenant (delegando ao
Provisioning Service, como `admin/use_cases/create_tenant_use_case.py`) e, em seguida,
autentica a pessoa imediatamente — mesma cauda de emissão de tokens de
`login_use_case.py`, sem verificar senha (acabou de ser criada)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from veloai_shared.exceptions import RateLimitedError

from app.core.config import Settings
from app.core.database import TenantConnectionManager
from app.core.provisioning_client import ProvisioningClient
from app.core.rate_limit import SignupRateLimiter
from app.modules.auth.repositories.refresh_token_repository import RefreshTokenRepository
from app.modules.auth.repositories.user_repository import TenantUserRepository
from app.modules.auth.schemas.auth import SignupRequest
from app.modules.auth.services.token_service import TokenService
from app.modules.auth.use_cases.login_use_case import LoginResult


class SignupUseCase:
    def __init__(
        self,
        *,
        settings: Settings,
        connection_manager: TenantConnectionManager,
        token_service: TokenService,
        provisioning_client: ProvisioningClient,
        rate_limiter: SignupRateLimiter,
    ) -> None:
        self._settings = settings
        self._connections = connection_manager
        self._tokens = token_service
        self._provisioning = provisioning_client
        self._rate_limiter = rate_limiter

    async def execute(
        self, *, payload: SignupRequest, ip: str | None, user_agent: str | None
    ) -> LoginResult:
        rate_limit_key = ip or "unknown"
        if await self._rate_limiter.is_blocked(rate_limit_key):
            raise RateLimitedError(
                "Muitos cadastros a partir deste endereço. Tente novamente mais tarde."
            )
        await self._rate_limiter.register_attempt(rate_limit_key)

        data = await self._provisioning.create_tenant(
            {
                "legal_name": payload.legal_name,
                "trade_name": payload.trade_name,
                "document": payload.document,
                "admin_name": payload.admin_name,
                "admin_email": payload.admin_email,
                "password": payload.password,
            }
        )
        tenant_id = uuid.UUID(data["tenant_id"])
        database_name = data["database_name"]

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            user_repository = TenantUserRepository(session)
            user = await user_repository.get_by_email(payload.admin_email)
            assert user is not None  # acabou de ser criado pelo Provisioning Service

            role = await user_repository.get_role_name(user.role_id) or ""
            permissions = await user_repository.get_role_permissions(user.role_id)

            access_token = self._tokens.issue_access_token(
                user_id=user.id, tenant_id=tenant_id, database_name=database_name, role=role
            )
            refresh_token = self._tokens.issue_refresh_token(
                user_id=user.id, tenant_id=tenant_id, database_name=database_name
            )

            refresh_repository = RefreshTokenRepository(session)
            await refresh_repository.create(
                user_id=user.id,
                token_hash=self._tokens.hash_refresh_token(refresh_token),
                expires_at=datetime.now(UTC)
                + timedelta(days=self._settings.jwt_refresh_token_expire_days),
                user_agent=user_agent,
                ip=ip,
            )

            await user_repository.touch_last_login(user)
            await session.commit()

        return LoginResult(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=role,
            permissions=permissions,
            must_change_password=False,
            tenant_name=payload.trade_name or payload.legal_name,
            avatar_url=None,  # usuário acabou de ser criado — nunca teve chance de enviar foto
        )
