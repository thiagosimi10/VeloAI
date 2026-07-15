"""Caso de uso: excluir fornecedor (soft delete — nunca exclusão física, conforme
00-AI-CONSTITUTION.md)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.suppliers.repositories.supplier_repository import SupplierRepository
from app.modules.suppliers.use_cases._helpers import serialize_supplier


class DeleteSupplierUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        supplier_id: uuid.UUID,
    ) -> None:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = SupplierRepository(session)
            supplier = await repository.get_by_id(supplier_id)
            if supplier is None:
                raise NotFoundError("Fornecedor não encontrado.", code="SUPPLIER_NOT_FOUND")

            before = serialize_supplier(supplier)
            await repository.soft_delete(supplier)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SUPPLIER_DELETED",
                resource="suppliers",
                before=before,
            )
            await session.commit()
