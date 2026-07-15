"""Caso de uso: remover um item de uma Ordem de Serviço — só permitido enquanto a OS
ainda não foi concluída/cancelada (nenhum estoque foi consumido para itens de produto,
já que o consumo só acontece no fechamento — ver `close_service_order_use_case.py`)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.service_orders.repositories.service_order_item_repository import (
    ServiceOrderItemRepository,
)
from app.modules.service_orders.repositories.service_order_repository import (
    ServiceOrderRepository,
)
from app.modules.service_orders.use_cases._helpers import (
    ensure_items_are_editable,
    recalculate_order_total,
)


class RemoveServiceOrderItemUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        order_id: uuid.UUID,
        item_id: uuid.UUID,
    ) -> None:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            order_repository = ServiceOrderRepository(session)
            order = await order_repository.get_by_id(order_id)
            if order is None:
                raise NotFoundError(
                    "Ordem de Serviço não encontrada.", code="SERVICE_ORDER_NOT_FOUND"
                )
            ensure_items_are_editable(order)

            item_repository = ServiceOrderItemRepository(session)
            item = await item_repository.get_by_id(item_id)
            if item is None or item.service_order_id != order_id:
                raise NotFoundError("Item não encontrado.", code="SERVICE_ORDER_ITEM_NOT_FOUND")

            await item_repository.delete(item)
            new_total = await recalculate_order_total(session, order, item_repository)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SERVICE_ORDER_ITEM_REMOVED",
                resource="service_orders",
                before={"item_id": str(item_id), "order_total": str(new_total)},
            )
            await session.commit()
