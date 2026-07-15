"""Caso de uso: cancelar uma Venda (`open` → `cancelled`). Como nenhum estoque é
consumido antes da conclusão (ver plano da Fase 9), cancelar não precisa estornar
nada."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.sales.repositories.sale_repository import SaleRepository
from app.modules.sales.schemas.sale import SaleResponse
from app.modules.sales.use_cases._helpers import (
    ensure_transition_allowed,
    serialize_sale,
    to_response,
)


class CancelSaleUseCase:
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
            repository = SaleRepository(session)
            sale = await repository.get_by_id(sale_id)
            if sale is None:
                raise NotFoundError("Venda não encontrada.", code="SALE_NOT_FOUND")
            ensure_transition_allowed(sale, "cancelled")

            before = serialize_sale(sale)
            await repository.update(sale, {"status": "cancelled"})

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SALE_CANCELLED",
                resource="sales",
                before=before,
                after=serialize_sale(sale),
            )
            await session.commit()

            return to_response(sale)
