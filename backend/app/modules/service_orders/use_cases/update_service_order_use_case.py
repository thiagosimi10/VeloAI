"""Caso de uso: atualizar dados gerais de uma Ordem de Serviço (nunca `number`/
`status`/`total`, que mudam por regras/ações próprias)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.service_orders.repositories.service_order_repository import (
    ServiceOrderRepository,
)
from app.modules.service_orders.schemas.service_order import (
    ServiceOrderResponse,
    UpdateServiceOrderRequest,
)
from app.modules.service_orders.use_cases._helpers import serialize_order, to_response
from app.modules.users.use_cases.get_user_use_case import GetUserUseCase


class UpdateServiceOrderUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        order_id: uuid.UUID,
        payload: UpdateServiceOrderRequest,
    ) -> ServiceOrderResponse:
        if payload.technician_id is not None:
            await GetUserUseCase(connection_manager=self._connections).execute(
                tenant_id=tenant_id, database_name=database_name, user_id=payload.technician_id
            )

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = ServiceOrderRepository(session)
            order = await repository.get_by_id(order_id)
            if order is None:
                raise NotFoundError(
                    "Ordem de Serviço não encontrada.", code="SERVICE_ORDER_NOT_FOUND"
                )

            before = serialize_order(order)
            update_data = payload.model_dump(exclude_unset=True)
            await repository.update(order, update_data)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SERVICE_ORDER_UPDATED",
                resource="service_orders",
                before=before,
                after=serialize_order(order),
            )
            await session.commit()

            return to_response(order)
