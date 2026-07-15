"""Caso de uso: iniciar o atendimento de uma Ordem de Serviço (`open` → `in_progress`)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.service_orders.repositories.service_order_repository import (
    ServiceOrderRepository,
)
from app.modules.service_orders.schemas.service_order import ServiceOrderResponse
from app.modules.service_orders.use_cases._helpers import (
    ensure_transition_allowed,
    serialize_order,
    to_response,
)


class StartServiceOrderUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        order_id: uuid.UUID,
    ) -> ServiceOrderResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = ServiceOrderRepository(session)
            order = await repository.get_by_id(order_id)
            if order is None:
                raise NotFoundError(
                    "Ordem de Serviço não encontrada.", code="SERVICE_ORDER_NOT_FOUND"
                )
            ensure_transition_allowed(order, "in_progress")

            before = serialize_order(order)
            await repository.update(order, {"status": "in_progress"})

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SERVICE_ORDER_STARTED",
                resource="service_orders",
                before=before,
                after=serialize_order(order),
            )
            await session.commit()

            return to_response(order)
