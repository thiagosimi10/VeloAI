"""Caso de uso: criar categoria. Garante nome único, conforme
05-BANCO-DE-DADOS.md."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import ConflictError
from veloai_shared.schema.tenant import Category

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.categories.repositories.category_repository import CategoryRepository
from app.modules.categories.schemas.category import CategoryResponse, CreateCategoryRequest
from app.modules.categories.use_cases._helpers import serialize_category


class CreateCategoryUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        payload: CreateCategoryRequest,
    ) -> CategoryResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = CategoryRepository(session)

            existing = await repository.get_by_name(payload.name)
            if existing is not None:
                raise ConflictError(
                    "Já existe uma categoria com este nome.",
                    code="CATEGORY_NAME_ALREADY_EXISTS",
                )

            category = Category(**payload.model_dump())
            await repository.create(category)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="CATEGORY_CREATED",
                resource="categories",
                after=serialize_category(category),
            )
            await session.commit()

            return CategoryResponse.model_validate(category)
