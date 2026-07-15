"""Caso de uso: excluir cliente (soft delete — nunca exclusão física, conforme
00-AI-CONSTITUTION.md)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.customers.repositories.customer_repository import CustomerRepository
from app.modules.customers.use_cases._helpers import serialize_customer


class DeleteCustomerUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        customer_id: uuid.UUID,
    ) -> None:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = CustomerRepository(session)
            customer = await repository.get_by_id(customer_id)
            if customer is None:
                raise NotFoundError("Cliente não encontrado.", code="CUSTOMER_NOT_FOUND")

            before = serialize_customer(customer)
            await repository.soft_delete(customer)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="CUSTOMER_DELETED",
                resource="customers",
                before=before,
            )
            await session.commit()
