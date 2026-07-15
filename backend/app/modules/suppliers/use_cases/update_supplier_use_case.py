"""Caso de uso: atualizar fornecedor (atualização parcial)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.suppliers.repositories.supplier_repository import SupplierRepository
from app.modules.suppliers.schemas.supplier import SupplierResponse, UpdateSupplierRequest
from app.modules.suppliers.use_cases._helpers import serialize_supplier


class UpdateSupplierUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        supplier_id: uuid.UUID,
        payload: UpdateSupplierRequest,
    ) -> SupplierResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = SupplierRepository(session)
            supplier = await repository.get_by_id(supplier_id)
            if supplier is None:
                raise NotFoundError("Fornecedor não encontrado.", code="SUPPLIER_NOT_FOUND")

            before = serialize_supplier(supplier)
            update_data = payload.model_dump(exclude_unset=True)
            await repository.update(supplier, update_data)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SUPPLIER_UPDATED",
                resource="suppliers",
                before=before,
                after=serialize_supplier(supplier),
            )
            await session.commit()

            return SupplierResponse.model_validate(supplier)
