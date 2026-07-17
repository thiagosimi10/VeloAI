"""Caso de uso: login de Platform Admin. Mesmo espírito de `auth/use_cases/
login_use_case.py` (rate limit + hash de senha), mas sem resolução de tenant, sem
refresh token e sem histórico de login — sessão simples de um único access token."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from veloai_shared.exceptions import AuthenticationError, RateLimitedError
from veloai_shared.security import verify_password

from app.core.database import get_master_session
from app.core.rate_limit import LoginRateLimiter
from app.modules.admin.repositories.admin_repository import AdminRepository
from app.modules.admin.services.platform_admin_token_service import PlatformAdminTokenService


@dataclass(frozen=True)
class PlatformAdminLoginResult:
    token: str
    admin_id: uuid.UUID
    email: str
    first_name: str
    last_name: str | None
    must_change_password: bool


class LoginPlatformAdminUseCase:
    def __init__(
        self,
        *,
        token_service: PlatformAdminTokenService,
        rate_limiter: LoginRateLimiter,
    ) -> None:
        self._tokens = token_service
        self._rate_limiter = rate_limiter

    async def execute(
        self, *, email: str, password: str, ip: str | None
    ) -> PlatformAdminLoginResult:
        rate_limit_key = f"admin:{email}:{ip or 'unknown'}"
        if await self._rate_limiter.is_blocked(rate_limit_key):
            raise RateLimitedError("Muitas tentativas de login. Tente novamente mais tarde.")

        async with get_master_session() as session:
            repository = AdminRepository(session)
            admin = await repository.get_platform_admin_by_email(email)

            if (
                admin is None
                or not admin.active
                or not verify_password(password, admin.password_hash)
            ):
                await self._rate_limiter.register_failed_attempt(rate_limit_key)
                raise AuthenticationError(
                    "E-mail ou senha inválidos.", code="INVALID_CREDENTIALS"
                )

            token = self._tokens.issue_token(admin_id=admin.id)

        await self._rate_limiter.reset(rate_limit_key)

        return PlatformAdminLoginResult(
            token=token,
            admin_id=admin.id,
            email=admin.email,
            first_name=admin.first_name,
            last_name=admin.last_name,
            must_change_password=admin.force_password_change,
        )
