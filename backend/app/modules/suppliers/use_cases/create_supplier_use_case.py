"""Caso de uso: criar fornecedor. Gera o `code` sequencial e garante documento único,
conforme 05-BANCO-DE-DADOS.md ("Mesmo padrão dos clientes")."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import ConflictError
from veloai_shared.schema.tenant import Supplier

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.suppliers.repositories.supplier_repository import SupplierRepository
from app.modules.suppliers.schemas.supplier import CreateSupplierRequest, SupplierResponse
from app.modules.suppliers.use_cases._helpers import serialize_supplier


class CreateSupplierUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        payload: CreateSupplierRequest,
    ) -> SupplierResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = SupplierRepository(session)

            existing = await repository.get_by_document(payload.document)
            if existing is not None:
                raise ConflictError(
                    "Já existe um fornecedor com este documento.",
                    code="SUPPLIER_DOCUMENT_ALREADY_EXISTS",
                )

            sequence = await repository.count_all() + 1
            supplier = Supplier(code=f"F{sequence:06d}", **payload.model_dump())
            await repository.create(supplier)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SUPPLIER_CREATED",
                resource="suppliers",
                after=serialize_supplier(supplier),
            )
            await session.commit()

            return SupplierResponse.model_validate(supplier)
