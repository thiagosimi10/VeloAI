"""Dependências reutilizáveis de autenticação e autorização (RBAC), conforme
16-BACKEND-ARCHITECTURE.md ("Autorização: RBAC, Permissões granulares. Nunca validar
permissões no Frontend.").

Todo módulo de negócio futuro deverá reutilizar `get_current_user`/`require_permission`
em vez de reimplementar extração de usuário ou checagem de permissão."""

from __future__ import annotations

import uuid
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from fastapi import Depends, Request
from veloai_shared.exceptions import AuthenticationError, PermissionDeniedError
from veloai_shared.security.jwt import TokenError

from app.core.config import Settings, get_settings
from app.core.database import (
    TenantConnectionManager,
    get_master_session,
    get_tenant_connection_manager,
)
from app.modules.auth.repositories.user_repository import TenantUserRepository
from app.modules.auth.services.token_service import TokenService
from app.modules.billing.services.subscription_gate_service import ensure_subscription_active

ACCESS_TOKEN_COOKIE_NAME = "access_token"
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"


@dataclass(frozen=True)
class CurrentUser:
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    database_name: str
    role: str


def get_token_service(settings: Settings = Depends(get_settings)) -> TokenService:
    return TokenService(settings)


async def get_current_user(
    request: Request,
    token_service: TokenService = Depends(get_token_service),
) -> CurrentUser:
    """Extrai e valida o access token do cookie HttpOnly. Nunca aceita o token via
    LocalStorage/header custom — apenas cookie, conforme 17-FRONTEND-ARCHITECTURE.md."""

    token = request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    if not token:
        raise AuthenticationError("Não autenticado.", code="NOT_AUTHENTICATED")

    try:
        claims = token_service.decode_access_token(token)
    except TokenError as exc:
        raise AuthenticationError(
            "Sessão inválida ou expirada.", code="SESSION_EXPIRED"
        ) from exc

    return CurrentUser(
        user_id=claims.user_id,
        tenant_id=claims.tenant_id,
        database_name=claims.database_name,
        role=claims.role,
    )


def require_permission(
    permission_code: str,
) -> Callable[..., Coroutine[Any, Any, CurrentUser]]:
    """Dependency factory de RBAC. Uso em uma rota de módulo futuro:

    ```python
    @router.post("/customers", dependencies=[Depends(require_permission("customers.create"))])
    ```

    A permissão é sempre revalidada contra o banco do tenant a cada requisição — nunca
    confiamos apenas no `role` embutido no token."""

    async def _dependency(
        current_user: CurrentUser = Depends(get_current_user),
        connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
    ) -> CurrentUser:
        async with connection_manager.session_for_tenant(
            current_user.tenant_id, current_user.database_name
        ) as session:
            permissions = await TenantUserRepository(session).get_role_permissions_by_name(
                current_user.role
            )

        if permission_code not in permissions:
            raise PermissionDeniedError(
                f"Permissão '{permission_code}' necessária.", code="PERMISSION_DENIED"
            )

        return current_user

    return _dependency


async def require_active_subscription(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Bloqueia o acesso de tenants com assinatura expirada/cancelada/suspensa,
    conforme 31-BILLING.md. Aplicada por rota via `dependencies=[...]` em
    `app/api/v1/router.py` — nunca em `auth_router` (login precisa sempre funcionar)
    nem no próprio `billing_router` (o tenant precisa continuar enxergando/cancelando a
    assinatura mesmo depois de bloqueado)."""

    async with get_master_session() as session:
        await ensure_subscription_active(session, current_user.tenant_id)

    return current_user
