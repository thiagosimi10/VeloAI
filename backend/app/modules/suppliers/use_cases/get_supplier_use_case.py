"""Caso de uso: buscar um fornecedor pelo id."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.database import TenantConnectionManager
from app.modules.suppliers.repositories.supplier_repository import SupplierRepository
from app.modules.suppliers.schemas.supplier import SupplierResponse


class GetSupplierUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, supplier_id: uuid.UUID
    ) -> SupplierResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            supplier = await SupplierRepository(session).get_by_id(supplier_id)
            if supplier is None:
                raise NotFoundError("Fornecedor não encontrado.", code="SUPPLIER_NOT_FOUND")
            return SupplierResponse.model_validate(supplier)
