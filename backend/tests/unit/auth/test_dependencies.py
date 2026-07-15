import uuid
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Request
from veloai_shared.exceptions import AuthenticationError, PermissionDeniedError

from app.core.config import Settings
from app.core.dependencies import (
    ACCESS_TOKEN_COOKIE_NAME,
    CurrentUser,
    get_current_user,
    require_permission,
)
from app.modules.auth.services.token_service import TokenService


def _make_request(cookies: dict[str, str]) -> Request:
    scope = {
        "type": "http",
        "headers": [
            (b"cookie", "; ".join(f"{k}={v}" for k, v in cookies.items()).encode()),
        ],
    }
    return Request(scope)


def _connection_manager_returning(session: AsyncMock) -> MagicMock:
    @asynccontextmanager
    async def _session_context(*_args: object, **_kwargs: object):
        yield session

    manager = MagicMock()
    manager.session_for_tenant = MagicMock(side_effect=_session_context)
    return manager


@pytest.fixture
def settings() -> Settings:
    return Settings(_env_file=None, jwt_secret="access-secret")  # type: ignore[call-arg]


@pytest.fixture
def token_service(settings: Settings) -> TokenService:
    return TokenService(settings)


async def test_get_current_user_raises_without_cookie(token_service: TokenService) -> None:
    request = _make_request({})

    with pytest.raises(AuthenticationError):
        await get_current_user(request, token_service=token_service)


async def test_get_current_user_raises_with_invalid_token(token_service: TokenService) -> None:
    request = _make_request({ACCESS_TOKEN_COOKIE_NAME: "not-a-valid-jwt"})

    with pytest.raises(AuthenticationError):
        await get_current_user(request, token_service=token_service)


async def test_get_current_user_returns_current_user_for_valid_token(
    token_service: TokenService,
) -> None:
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    token = token_service.issue_access_token(
        user_id=user_id, tenant_id=tenant_id, database_name="tenant_abc", role="Administrador"
    )
    request = _make_request({ACCESS_TOKEN_COOKIE_NAME: token})

    current_user = await get_current_user(request, token_service=token_service)

    assert current_user.user_id == user_id
    assert current_user.tenant_id == tenant_id
    assert current_user.database_name == "tenant_abc"
    assert current_user.role == "Administrador"


async def test_require_permission_allows_when_permission_present() -> None:
    dependency = require_permission("system.admin")
    connection_manager = _connection_manager_returning(AsyncMock())
    current_user = CurrentUser(
        user_id=uuid.uuid4(), tenant_id=uuid.uuid4(), database_name="tenant_abc", role="Admin"
    )

    with patch(
        "app.core.dependencies.TenantUserRepository.get_role_permissions_by_name",
        AsyncMock(return_value=["system.admin"]),
    ):
        result = await dependency(
            current_user=current_user, connection_manager=connection_manager
        )

    assert result is current_user


async def test_require_permission_denies_when_permission_missing() -> None:
    dependency = require_permission("system.admin")
    connection_manager = _connection_manager_returning(AsyncMock())
    current_user = CurrentUser(
        user_id=uuid.uuid4(), tenant_id=uuid.uuid4(), database_name="tenant_abc", role="Vendedor"
    )

    with (
        patch(
            "app.core.dependencies.TenantUserRepository.get_role_permissions_by_name",
            AsyncMock(return_value=[]),
        ),
        pytest.raises(PermissionDeniedError),
    ):
        await dependency(current_user=current_user, connection_manager=connection_manager)
