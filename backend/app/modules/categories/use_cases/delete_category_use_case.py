"""Caso de uso: excluir categoria (soft delete — nunca exclusão física, conforme
00-AI-CONSTITUTION.md)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.categories.repositories.category_repository import CategoryRepository
from app.modules.categories.use_cases._helpers import serialize_category


class DeleteCategoryUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        category_id: uuid.UUID,
    ) -> None:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = CategoryRepository(session)
            category = await repository.get_by_id(category_id)
            if category is None:
                raise NotFoundError("Categoria não encontrada.", code="CATEGORY_NOT_FOUND")

            before = serialize_category(category)
            await repository.soft_delete(category)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="CATEGORY_DELETED",
                resource="categories",
                before=before,
            )
            await session.commit()
