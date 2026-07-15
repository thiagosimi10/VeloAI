"""Caso de uso: Refresh Token. Valida o refresh token, rotaciona (revoga o antigo e
emite um novo par), conforme 16-BACKEND-ARCHITECTURE.md ("Rotação automática,
Blacklist.")."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from veloai_shared.exceptions import AuthenticationError
from veloai_shared.security.jwt import TokenError

from app.core.config import Settings
from app.core.database import TenantConnectionManager
from app.modules.auth.repositories.refresh_token_repository import RefreshTokenRepository
from app.modules.auth.repositories.user_repository import TenantUserRepository
from app.modules.auth.services.token_service import TokenService


@dataclass(frozen=True)
class RefreshResult:
    access_token: str
    refresh_token: str


class RefreshUseCase:
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

    async def execute(self, *, refresh_token: str) -> RefreshResult:
        try:
            claims = self._tokens.decode_refresh_token(refresh_token)
        except TokenError as exc:
            raise AuthenticationError(
                "Sessão expirada. Faça login novamente.", code="REFRESH_TOKEN_INVALID"
            ) from exc

        token_hash = self._tokens.hash_refresh_token(refresh_token)

        async with self._connections.session_for_tenant(
            claims.tenant_id, claims.database_name
        ) as session:
            refresh_repository = RefreshTokenRepository(session)
            stored_token = await refresh_repository.get_valid_by_hash(token_hash)
            if stored_token is None:
                raise AuthenticationError(
                    "Sessão expirada. Faça login novamente.", code="REFRESH_TOKEN_INVALID"
                )

            user_repository = TenantUserRepository(session)
            user = await user_repository.get_by_id(claims.user_id)
            if user is None or not user.active:
                raise AuthenticationError(
                    "Usuário inativo ou não encontrado.", code="REFRESH_TOKEN_INVALID"
                )

            role = await user_repository.get_role_name(user.role_id) or ""

            await refresh_repository.revoke(stored_token)

            new_access_token = self._tokens.issue_access_token(
                user_id=user.id,
                tenant_id=claims.tenant_id,
                database_name=claims.database_name,
                role=role,
            )
            new_refresh_token = self._tokens.issue_refresh_token(
                user_id=user.id, tenant_id=claims.tenant_id, database_name=claims.database_name
            )

            await refresh_repository.create(
                user_id=user.id,
                token_hash=self._tokens.hash_refresh_token(new_refresh_token),
                expires_at=datetime.now(UTC)
                + timedelta(days=self._settings.jwt_refresh_token_expire_days),
                user_agent=stored_token.user_agent,
                ip=stored_token.ip,
            )
            await session.commit()

        return RefreshResult(access_token=new_access_token, refresh_token=new_refresh_token)
