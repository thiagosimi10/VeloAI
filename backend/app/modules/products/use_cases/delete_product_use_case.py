"""Caso de uso: excluir produto (soft delete — nunca exclusão física, conforme
00-AI-CONSTITUTION.md)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.products.repositories.product_repository import ProductRepository
from app.modules.products.use_cases._helpers import serialize_product


class DeleteProductUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        product_id: uuid.UUID,
    ) -> None:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = ProductRepository(session)
            product = await repository.get_by_id(product_id)
            if product is None:
                raise NotFoundError("Produto não encontrado.", code="PRODUCT_NOT_FOUND")

            before = serialize_product(product)
            await repository.soft_delete(product)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="PRODUCT_DELETED",
                resource="products",
                before=before,
            )
            await session.commit()
