"""Caso de uso: buscar uma categoria pelo id."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.database import TenantConnectionManager
from app.modules.categories.repositories.category_repository import CategoryRepository
from app.modules.categories.schemas.category import CategoryResponse


class GetCategoryUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, category_id: uuid.UUID
    ) -> CategoryResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            category = await CategoryRepository(session).get_by_id(category_id)
            if category is None:
                raise NotFoundError("Categoria não encontrada.", code="CATEGORY_NOT_FOUND")
            return CategoryResponse.model_validate(category)
