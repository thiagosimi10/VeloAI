"""Caso de uso: remover um item de uma Venda — só permitido enquanto ela ainda está
`open` (nenhum estoque foi consumido para itens de produto, já que o consumo só
acontece na conclusão — ver `complete_sale_use_case.py`)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.sales.repositories.sale_item_repository import SaleItemRepository
from app.modules.sales.repositories.sale_repository import SaleRepository
from app.modules.sales.use_cases._helpers import ensure_sale_is_editable, recalculate_sale_total


class RemoveSaleItemUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        sale_id: uuid.UUID,
        item_id: uuid.UUID,
    ) -> None:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            sale_repository = SaleRepository(session)
            sale = await sale_repository.get_by_id(sale_id)
            if sale is None:
                raise NotFoundError("Venda não encontrada.", code="SALE_NOT_FOUND")
            ensure_sale_is_editable(sale)

            item_repository = SaleItemRepository(session)
            item = await item_repository.get_by_id(item_id)
            if item is None or item.sale_id != sale_id:
                raise NotFoundError("Item não encontrado.", code="SALE_ITEM_NOT_FOUND")

            await item_repository.delete(item)
            new_total = await recalculate_sale_total(session, sale, item_repository)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SALE_ITEM_REMOVED",
                resource="sales",
                before={"item_id": str(item_id), "sale_total": str(new_total)},
            )
            await session.commit()
