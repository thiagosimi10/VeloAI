"""Caso de uso: Login. Orquestra rate limit, resolução de tenant (Banco Master),
autenticação, emissão de tokens e auditoria, conforme 04-MULTI-TENANCY.md ("Login →
Banco Master → Localiza Tenant → ...") e 29-SECURITY.md."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from veloai_shared.exceptions import AuthenticationError, RateLimitedError
from veloai_shared.security import verify_password

from app.core.config import Settings
from app.core.database import TenantConnectionManager
from app.core.rate_limit import LoginRateLimiter
from app.modules.auth.repositories.login_history_repository import LoginHistoryRepository
from app.modules.auth.repositories.refresh_token_repository import RefreshTokenRepository
from app.modules.auth.repositories.user_repository import TenantUserRepository
from app.modules.auth.services.token_service import TokenService


@dataclass(frozen=True)
class LoginResult:
    access_token: str
    refresh_token: str
    user_id: uuid.UUID
    email: str
    first_name: str
    last_name: str | None
    role: str
    permissions: list[str]
    must_change_password: bool


class LoginUseCase:
    def __init__(
        self,
        *,
        settings: Settings,
        connection_manager: TenantConnectionManager,
        token_service: TokenService,
        rate_limiter: LoginRateLimiter,
    ) -> None:
        self._settings = settings
        self._connections = connection_manager
        self._tokens = token_service
        self._rate_limiter = rate_limiter

    async def execute(
        self, *, email: str, password: str, ip: str | None, user_agent: str | None
    ) -> LoginResult:
        rate_limit_key = f"{email}:{ip or 'unknown'}"
        if await self._rate_limiter.is_blocked(rate_limit_key):
            raise RateLimitedError("Muitas tentativas de login. Tente novamente mais tarde.")

        tenant = await self._connections.resolve_tenant_by_email(email)
        if tenant is None:
            await self._rate_limiter.register_failed_attempt(rate_limit_key)
            raise AuthenticationError("E-mail ou senha inválidos.", code="INVALID_CREDENTIALS")

        async with self._connections.session_for_tenant(
            tenant.id, tenant.database_name
        ) as session:
            user_repository = TenantUserRepository(session)
            login_history = LoginHistoryRepository(session)
            user = await user_repository.get_by_email(email)

            if user is None or not user.active or not verify_password(password, user.password_hash):
                await login_history.record(
                    user_id=user.id if user else None,
                    email=email,
                    success=False,
                    ip=ip,
                    user_agent=user_agent,
                )
                await session.commit()
                await self._rate_limiter.register_failed_attempt(rate_limit_key)
                raise AuthenticationError(
                    "E-mail ou senha inválidos.", code="INVALID_CREDENTIALS"
                )

            role = await user_repository.get_role_name(user.role_id) or ""
            permissions = await user_repository.get_role_permissions(user.role_id)

            access_token = self._tokens.issue_access_token(
                user_id=user.id,
                tenant_id=tenant.id,
                database_name=tenant.database_name,
                role=role,
            )
            refresh_token = self._tokens.issue_refresh_token(
                user_id=user.id, tenant_id=tenant.id, database_name=tenant.database_name
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
            await login_history.record(
                user_id=user.id, email=email, success=True, ip=ip, user_agent=user_agent
            )
            await session.commit()

        await self._rate_limiter.reset(rate_limit_key)

        return LoginResult(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=role,
            permissions=permissions,
            must_change_password=user.force_password_change,
        )
