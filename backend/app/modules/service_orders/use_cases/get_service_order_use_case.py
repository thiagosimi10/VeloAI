"""Caso de uso: buscar uma Ordem de Serviço pelo id, com os itens embutidos."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.database import TenantConnectionManager
from app.modules.service_orders.repositories.service_order_item_repository import (
    ServiceOrderItemRepository,
)
from app.modules.service_orders.repositories.service_order_repository import (
    ServiceOrderRepository,
)
from app.modules.service_orders.schemas.service_order import ServiceOrderResponse
from app.modules.service_orders.use_cases._helpers import build_order_response


class GetServiceOrderUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, order_id: uuid.UUID
    ) -> ServiceOrderResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            order = await ServiceOrderRepository(session).get_by_id(order_id)
            if order is None:
                raise NotFoundError(
                    "Ordem de Serviço não encontrada.", code="SERVICE_ORDER_NOT_FOUND"
                )
            return await build_order_response(order, ServiceOrderItemRepository(session))
