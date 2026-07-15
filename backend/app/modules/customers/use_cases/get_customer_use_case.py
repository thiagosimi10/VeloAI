"""Caso de uso: buscar um cliente pelo id."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.database import TenantConnectionManager
from app.modules.customers.repositories.customer_repository import CustomerRepository
from app.modules.customers.schemas.customer import CustomerResponse


class GetCustomerUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, customer_id: uuid.UUID
    ) -> CustomerResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            customer = await CustomerRepository(session).get_by_id(customer_id)
            if customer is None:
                raise NotFoundError("Cliente não encontrado.", code="CUSTOMER_NOT_FOUND")
            return CustomerResponse.model_validate(customer)
