"""Caso de uso: concluir uma Ordem de Serviço (`in_progress` → `completed`). Exige
técnico responsável (10-ORDEM-DE-SERVICO.md: "Não permitir concluir OS sem técnico
responsável") e consome o estoque de cada item-produto automaticamente
(10-ORDEM-DE-SERVICO.md + 09-PRODUTOS.md) — tudo em uma única transação, reaproveitando
`apply_stock_movement` (`products/services/stock_movement_service.py`) para não abrir
uma sessão por produto."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from veloai_shared.exceptions import NotFoundError, ValidationError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.products.services.stock_movement_service import apply_stock_movement
from app.modules.service_orders.repositories.service_order_item_repository import (
    ServiceOrderItemRepository,
)
from app.modules.service_orders.repositories.service_order_repository import (
    ServiceOrderRepository,
)
from app.modules.service_orders.schemas.service_order import (
    CloseServiceOrderRequest,
    ServiceOrderResponse,
)
from app.modules.service_orders.use_cases._helpers import (
    ensure_transition_allowed,
    serialize_order,
    to_response,
)
from app.modules.users.use_cases.get_user_use_case import GetUserUseCase


class CloseServiceOrderUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        order_id: uuid.UUID,
        payload: CloseServiceOrderRequest,
    ) -> ServiceOrderResponse:
        if payload.technician_id is not None:
            await GetUserUseCase(connection_manager=self._connections).execute(
                tenant_id=tenant_id, database_name=database_name, user_id=payload.technician_id
            )

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            order_repository = ServiceOrderRepository(session)
            order = await order_repository.get_by_id(order_id)
            if order is None:
                raise NotFoundError(
                    "Ordem de Serviço não encontrada.", code="SERVICE_ORDER_NOT_FOUND"
                )
            ensure_transition_allowed(order, "completed")

            technician_id = payload.technician_id or order.technician_id
            if technician_id is None:
                raise ValidationError(
                    "Não é possível concluir uma Ordem de Serviço sem técnico responsável.",
                    code="SERVICE_ORDER_TECHNICIAN_REQUIRED",
                )

            before = serialize_order(order)

            item_repository = ServiceOrderItemRepository(session)
            items = await item_repository.list_all_by_order(order_id)
            for item in items:
                if item.product_id is not None:
                    await apply_stock_movement(
                        session,
                        product_id=item.product_id,
                        movement="out",
                        quantity=item.quantity,
                        reason=f"Consumo automático pela Ordem de Serviço {order.number}",
                    )

            update_data: dict[str, object] = {
                "status": "completed",
                "technician_id": technician_id,
                "finished_at": datetime.now(UTC),
            }
            if payload.solution is not None:
                update_data["solution"] = payload.solution
            await order_repository.update(order, update_data)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SERVICE_ORDER_CLOSED",
                resource="service_orders",
                before=before,
                after=serialize_order(order),
            )
            await session.commit()

            return to_response(order)
