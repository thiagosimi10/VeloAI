"""Caso de uso: adicionar um item de produto a uma Venda. Valida a referência via
`GetProductUseCase` (nunca acessando o repository de outro módulo diretamente) e usa o
preço de catálogo (`sale_price`) quando `unit_price` não é informado."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError
from veloai_shared.schema.tenant import SaleItem

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.products.use_cases.get_product_use_case import GetProductUseCase
from app.modules.sales.repositories.sale_item_repository import SaleItemRepository
from app.modules.sales.repositories.sale_repository import SaleRepository
from app.modules.sales.schemas.sale_item import AddSaleItemRequest, SaleItemResponse
from app.modules.sales.use_cases._helpers import ensure_sale_is_editable, recalculate_sale_total


class AddSaleItemUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        sale_id: uuid.UUID,
        payload: AddSaleItemRequest,
    ) -> SaleItemResponse:
        product = await GetProductUseCase(connection_manager=self._connections).execute(
            tenant_id=tenant_id, database_name=database_name, product_id=payload.product_id
        )
        unit_price = payload.unit_price if payload.unit_price is not None else product.sale_price

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            sale_repository = SaleRepository(session)
            sale = await sale_repository.get_by_id(sale_id)
            if sale is None:
                raise NotFoundError("Venda não encontrada.", code="SALE_NOT_FOUND")
            ensure_sale_is_editable(sale)

            item_repository = SaleItemRepository(session)
            item = SaleItem(
                sale_id=sale_id,
                product_id=payload.product_id,
                quantity=payload.quantity,
                unit_price=unit_price,
            )
            await item_repository.create(item)
            new_total = await recalculate_sale_total(session, sale, item_repository)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SALE_ITEM_ADDED",
                resource="sales",
                after={"item_id": str(item.id), "sale_total": str(new_total)},
            )
            await session.commit()

            return SaleItemResponse.model_validate(item)
