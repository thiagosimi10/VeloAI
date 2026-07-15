"""Caso de uso: buscar uma Venda pelo id, com os itens embutidos."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.database import TenantConnectionManager
from app.modules.sales.repositories.sale_item_repository import SaleItemRepository
from app.modules.sales.repositories.sale_repository import SaleRepository
from app.modules.sales.schemas.sale import SaleResponse
from app.modules.sales.use_cases._helpers import build_sale_response


class GetSaleUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, sale_id: uuid.UUID
    ) -> SaleResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            sale = await SaleRepository(session).get_by_id(sale_id)
            if sale is None:
                raise NotFoundError("Venda não encontrada.", code="SALE_NOT_FOUND")
            return await build_sale_response(sale, SaleItemRepository(session))
