import uuid
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from veloai_shared.exceptions import NotFoundError

from app.modules.users.schemas.user import UserFilterParams
from app.modules.users.use_cases.get_user_use_case import GetUserUseCase
from app.modules.users.use_cases.list_users_use_case import ListUsersUseCase


def _connection_manager_with_session(session: AsyncMock) -> MagicMock:
    @asynccontextmanager
    async def _session_context(*_args: object, **_kwargs: object):
        yield session

    manager = MagicMock()
    manager.session_for_tenant = MagicMock(side_effect=_session_context)
    return manager


def _build_user_mock(**overrides: object) -> MagicMock:
    user = MagicMock()
    user.id = overrides.get("id", uuid.uuid4())
    user.first_name = overrides.get("first_name", "Carlos")
    user.last_name = overrides.get("last_name", "Souza")
    user.email = overrides.get("email", "carlos@empresa.test")
    user.active = overrides.get("active", True)
    return user


async def test_get_user_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = GetUserUseCase(connection_manager=connection_manager)

    with patch("app.modules.users.use_cases.get_user_use_case.UserRepository") as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(), database_name="tenant_abc", user_id=uuid.uuid4()
            )


async def test_list_users_computes_pagination_meta() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = ListUsersUseCase(connection_manager=connection_manager)
    user = _build_user_mock()

    with patch("app.modules.users.use_cases.list_users_use_case.UserRepository") as repo_cls:
        repo_cls.return_value.list = AsyncMock(return_value=([user], 25))

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            filters=UserFilterParams(page=1, page_size=10),
        )

    assert result.meta.total == 25
    assert result.meta.pages == 3
    assert len(result.items) == 1
    assert result.items[0].email == "carlos@empresa.test"
