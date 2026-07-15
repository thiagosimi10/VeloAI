"""Caso de uso: atualizar cliente (atualização parcial)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.customers.repositories.customer_repository import CustomerRepository
from app.modules.customers.schemas.customer import CustomerResponse, UpdateCustomerRequest
from app.modules.customers.use_cases._helpers import serialize_customer


class UpdateCustomerUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        customer_id: uuid.UUID,
        payload: UpdateCustomerRequest,
    ) -> CustomerResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = CustomerRepository(session)
            customer = await repository.get_by_id(customer_id)
            if customer is None:
                raise NotFoundError("Cliente não encontrado.", code="CUSTOMER_NOT_FOUND")

            before = serialize_customer(customer)
            update_data = payload.model_dump(exclude_unset=True)
            await repository.update(customer, update_data)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="CUSTOMER_UPDATED",
                resource="customers",
                before=before,
                after=serialize_customer(customer),
            )
            await session.commit()

            return CustomerResponse.model_validate(customer)
