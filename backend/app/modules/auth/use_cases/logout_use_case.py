"""Caso de uso: Logout. Revoga o refresh token corrente, conforme 29-SECURITY.md
("Revogação de Sessões")."""

from __future__ import annotations

from veloai_shared.security.jwt import TokenError

from app.core.database import TenantConnectionManager
from app.modules.auth.repositories.refresh_token_repository import RefreshTokenRepository
from app.modules.auth.services.token_service import TokenService


class LogoutUseCase:
    def __init__(
        self, *, connection_manager: TenantConnectionManager, token_service: TokenService
    ) -> None:
        self._connections = connection_manager
        self._tokens = token_service

    async def execute(self, *, refresh_token: str) -> None:
        try:
            claims = self._tokens.decode_refresh_token(refresh_token)
        except TokenError:
            # Token já inválido/expirado — nada a revogar, logout é sempre bem-sucedido
            # do ponto de vista do cliente (os cookies serão limpos de qualquer forma).
            return

        token_hash = self._tokens.hash_refresh_token(refresh_token)

        async with self._connections.session_for_tenant(
            claims.tenant_id, claims.database_name
        ) as session:
            refresh_repository = RefreshTokenRepository(session)
            stored_token = await refresh_repository.get_valid_by_hash(token_hash)
            if stored_token is not None:
                await refresh_repository.revoke(stored_token)
                await session.commit()
