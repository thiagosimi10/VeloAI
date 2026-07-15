"""Caso de uso: atualizar `discount`/`payment_method` de uma Venda — só permitido
enquanto `open` (depois de `paid`/`cancelled` a venda está financeiramente encerrada,
mesmo espírito de `ensure_sale_is_editable`). Nunca `status`/`total`, que mudam por
ações próprias (`complete`/`cancel`)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.sales.repositories.sale_item_repository import SaleItemRepository
from app.modules.sales.repositories.sale_repository import SaleRepository
from app.modules.sales.schemas.sale import SaleResponse, UpdateSaleRequest
from app.modules.sales.use_cases._helpers import (
    ensure_sale_is_editable,
    recalculate_sale_total,
    serialize_sale,
    to_response,
)


class UpdateSaleUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        sale_id: uuid.UUID,
        payload: UpdateSaleRequest,
    ) -> SaleResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = SaleRepository(session)
            sale = await repository.get_by_id(sale_id)
            if sale is None:
                raise NotFoundError("Venda não encontrada.", code="SALE_NOT_FOUND")
            ensure_sale_is_editable(sale)

            before = serialize_sale(sale)
            update_data = payload.model_dump(exclude_unset=True)
            await repository.update(sale, update_data)

            if "discount" in update_data:
                await recalculate_sale_total(session, sale, SaleItemRepository(session))

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SALE_UPDATED",
                resource="sales",
                before=before,
                after=serialize_sale(sale),
            )
            await session.commit()

            return to_response(sale)
