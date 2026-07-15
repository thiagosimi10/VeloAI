"""Caso de uso: concluir uma Venda (`open` → `paid`). Consome o estoque de cada item
automaticamente (09-PRODUTOS.md: "Toda Venda consumirá estoque automaticamente ao ser
finalizada") — tudo em uma única transação, reaproveitando `apply_stock_movement`
(`products/services/stock_movement_service.py`) exatamente como
`service_orders/use_cases/close_service_order_use_case.py` já faz, para não abrir uma
sessão por produto. "Não permitir venda de produto sem estoque" já é garantido pela
validação existente dentro do próprio serviço (`ConflictError` → 409)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.products.services.stock_movement_service import apply_stock_movement
from app.modules.sales.repositories.sale_item_repository import SaleItemRepository
from app.modules.sales.repositories.sale_repository import SaleRepository
from app.modules.sales.schemas.sale import SaleResponse
from app.modules.sales.use_cases._helpers import (
    ensure_transition_allowed,
    serialize_sale,
    to_response,
)


class CompleteSaleUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        sale_id: uuid.UUID,
    ) -> SaleResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            sale_repository = SaleRepository(session)
            sale = await sale_repository.get_by_id(sale_id)
            if sale is None:
                raise NotFoundError("Venda não encontrada.", code="SALE_NOT_FOUND")
            ensure_transition_allowed(sale, "paid")

            before = serialize_sale(sale)

            item_repository = SaleItemRepository(session)
            items = await item_repository.list_all_by_sale(sale_id)
            for item in items:
                await apply_stock_movement(
                    session,
                    product_id=item.product_id,
                    movement="out",
                    quantity=item.quantity,
                    reason=f"Consumo automático pela Venda {sale.id}",
                )

            await sale_repository.update(sale, {"status": "paid"})

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SALE_COMPLETED",
                resource="sales",
                before=before,
                after=serialize_sale(sale),
            )
            await session.commit()

            return to_response(sale)
