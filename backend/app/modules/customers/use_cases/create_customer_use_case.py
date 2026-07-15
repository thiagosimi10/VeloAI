"""Caso de uso: criar cliente. Gera o `code` sequencial e garante documento único,
conforme 08-CLIENTES.md ("CPF e CNPJ não poderão ser duplicados")."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import ConflictError
from veloai_shared.schema.tenant import Customer

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.customers.repositories.customer_repository import CustomerRepository
from app.modules.customers.schemas.customer import CreateCustomerRequest, CustomerResponse
from app.modules.customers.use_cases._helpers import serialize_customer


class CreateCustomerUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        payload: CreateCustomerRequest,
    ) -> CustomerResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = CustomerRepository(session)

            existing = await repository.get_by_document(payload.document)
            if existing is not None:
                raise ConflictError(
                    "Já existe um cliente com este documento.",
                    code="CUSTOMER_DOCUMENT_ALREADY_EXISTS",
                )

            sequence = await repository.count_all() + 1
            customer = Customer(code=f"C{sequence:06d}", **payload.model_dump())
            await repository.create(customer)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="CUSTOMER_CREATED",
                resource="customers",
                after=serialize_customer(customer),
            )
            await session.commit()

            return CustomerResponse.model_validate(customer)
