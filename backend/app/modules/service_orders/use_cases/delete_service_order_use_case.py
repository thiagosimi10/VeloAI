"""Caso de uso: excluir Ordem de Serviço (soft delete — nunca exclusão física, conforme
00-AI-CONSTITUTION.md)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.service_orders.repositories.service_order_repository import (
    ServiceOrderRepository,
)
from app.modules.service_orders.use_cases._helpers import serialize_order


class DeleteServiceOrderUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        order_id: uuid.UUID,
    ) -> None:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = ServiceOrderRepository(session)
            order = await repository.get_by_id(order_id)
            if order is None:
                raise NotFoundError(
                    "Ordem de Serviço não encontrada.", code="SERVICE_ORDER_NOT_FOUND"
                )

            before = serialize_order(order)
            await repository.soft_delete(order)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SERVICE_ORDER_DELETED",
                resource="service_orders",
                before=before,
            )
            await session.commit()
