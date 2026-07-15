import uuid
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from veloai_shared.exceptions import ConflictError, NotFoundError

from app.modules.categories.schemas.category import (
    CategoryFilterParams,
    CreateCategoryRequest,
    UpdateCategoryRequest,
)
from app.modules.categories.use_cases.create_category_use_case import CreateCategoryUseCase
from app.modules.categories.use_cases.delete_category_use_case import DeleteCategoryUseCase
from app.modules.categories.use_cases.get_category_use_case import GetCategoryUseCase
from app.modules.categories.use_cases.list_categories_use_case import ListCategoriesUseCase
from app.modules.categories.use_cases.update_category_use_case import UpdateCategoryUseCase


def _connection_manager_with_session(session: AsyncMock) -> MagicMock:
    @asynccontextmanager
    async def _session_context(*_args: object, **_kwargs: object):
        yield session

    manager = MagicMock()
    manager.session_for_tenant = MagicMock(side_effect=_session_context)
    return manager


def _build_category_mock(**overrides: object) -> MagicMock:
    category = MagicMock()
    category.id = overrides.get("id", uuid.uuid4())
    category.name = overrides.get("name", "Armazenamento")
    category.description = overrides.get("description", "SSDs e HDs")
    from datetime import UTC, datetime

    category.created_at = overrides.get("created_at") or datetime.now(UTC)
    category.updated_at = overrides.get("updated_at") or datetime.now(UTC)
    return category


async def test_list_categories_computes_pagination_meta() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = ListCategoriesUseCase(connection_manager=connection_manager)

    category = _build_category_mock()
    with patch(
        "app.modules.categories.use_cases.list_categories_use_case.CategoryRepository"
    ) as repo_cls:
        repo_cls.return_value.list = AsyncMock(return_value=([category], 25))

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            filters=CategoryFilterParams(page=1, page_size=10),
        )

    assert result.meta.total == 25
    assert result.meta.pages == 3
    assert len(result.items) == 1
    assert result.items[0].name == "Armazenamento"


async def test_get_category_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = GetCategoryUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.categories.use_cases.get_category_use_case.CategoryRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(), database_name="tenant_abc", category_id=uuid.uuid4()
            )


async def test_create_category_rejects_duplicate_name() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CreateCategoryUseCase(connection_manager=connection_manager)
    payload = CreateCategoryRequest(name="Armazenamento")

    with patch(
        "app.modules.categories.use_cases.create_category_use_case.CategoryRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_name = AsyncMock(return_value=_build_category_mock())

        with pytest.raises(ConflictError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                payload=payload,
            )


async def test_update_category_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = UpdateCategoryUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.categories.use_cases.update_category_use_case.CategoryRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                category_id=uuid.uuid4(),
                payload=UpdateCategoryRequest(name="Novo Nome"),
            )


async def test_update_category_rejects_rename_to_existing_name() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = UpdateCategoryUseCase(connection_manager=connection_manager)
    category = _build_category_mock(name="Armazenamento")

    with patch(
        "app.modules.categories.use_cases.update_category_use_case.CategoryRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=category)
        repo_cls.return_value.get_by_name = AsyncMock(return_value=_build_category_mock(name="Rede"))

        with pytest.raises(ConflictError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                category_id=category.id,
                payload=UpdateCategoryRequest(name="Rede"),
            )


async def test_delete_category_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = DeleteCategoryUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.categories.use_cases.delete_category_use_case.CategoryRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                category_id=uuid.uuid4(),
            )
