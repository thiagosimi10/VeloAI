"""Caso de uso: ajustar o estoque de um produto. Abre uma única sessão/transação,
delega o cálculo e a persistência a `stock_movement_service.apply_stock_movement`
(reaproveitado por `service_orders` ao concluir uma Ordem de Serviço) e grava a
auditoria genérica antes de comitar."""

from __future__ import annotations

import uuid

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.products.schemas.stock_movement import (
    CreateStockMovementRequest,
    StockMovementResponse,
)
from app.modules.products.services.stock_movement_service import apply_stock_movement


class AdjustProductStockUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        product_id: uuid.UUID,
        payload: CreateStockMovementRequest,
    ) -> StockMovementResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            movement = await apply_stock_movement(
                session,
                product_id=product_id,
                movement=payload.movement,
                quantity=payload.quantity,
                reason=payload.reason,
            )

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="PRODUCT_STOCK_ADJUSTED",
                resource="products",
                before={"stock": movement.previous_stock},
                after={"stock": movement.current_stock},
            )
            await session.commit()

            return StockMovementResponse.model_validate(movement)
