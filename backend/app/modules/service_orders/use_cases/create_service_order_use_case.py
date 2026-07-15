"""Caso de uso: criar Ordem de Serviço. Gera o `number` sequencial e garante que
`customer_id` exista e que `technician_id`, quando informado, aponte para um usuário
existente — reaproveitando `GetCustomerUseCase`/`GetUserUseCase` (nunca acessando o
repository de outro módulo diretamente, conforme `app/modules/README.md`)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from veloai_shared.schema.tenant import ServiceOrder

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.customers.use_cases.get_customer_use_case import GetCustomerUseCase
from app.modules.service_orders.repositories.service_order_repository import (
    ServiceOrderRepository,
)
from app.modules.service_orders.schemas.service_order import (
    CreateServiceOrderRequest,
    ServiceOrderResponse,
)
from app.modules.service_orders.use_cases._helpers import serialize_order, to_response
from app.modules.users.use_cases.get_user_use_case import GetUserUseCase


class CreateServiceOrderUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        payload: CreateServiceOrderRequest,
    ) -> ServiceOrderResponse:
        await GetCustomerUseCase(connection_manager=self._connections).execute(
            tenant_id=tenant_id, database_name=database_name, customer_id=payload.customer_id
        )
        if payload.technician_id is not None:
            await GetUserUseCase(connection_manager=self._connections).execute(
                tenant_id=tenant_id, database_name=database_name, user_id=payload.technician_id
            )

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = ServiceOrderRepository(session)

            sequence = await repository.count_all() + 1
            year = datetime.now(UTC).year
            order = ServiceOrder(
                number=f"OS-{year}-{sequence:06d}",
                customer_id=payload.customer_id,
                technician_id=payload.technician_id,
                equipment=payload.equipment,
                serial_number=payload.serial_number,
                problem=payload.problem,
            )
            await repository.create(order)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SERVICE_ORDER_CREATED",
                resource="service_orders",
                after=serialize_order(order),
            )
            await session.commit()

            return to_response(order)
