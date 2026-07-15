"""Caso de uso: adicionar um item (produto ou serviço) a uma Ordem de Serviço. Valida a
referência via `GetProductUseCase`/`GetServiceUseCase` (nunca acessando o repository de
outro módulo diretamente) e usa o preço de catálogo quando `unit_price` não é
informado."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError
from veloai_shared.schema.tenant import ServiceOrderItem

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.products.use_cases.get_product_use_case import GetProductUseCase
from app.modules.service_orders.repositories.service_order_item_repository import (
    ServiceOrderItemRepository,
)
from app.modules.service_orders.repositories.service_order_repository import (
    ServiceOrderRepository,
)
from app.modules.service_orders.schemas.service_order_item import (
    AddServiceOrderItemRequest,
    ServiceOrderItemResponse,
)
from app.modules.service_orders.use_cases._helpers import (
    build_item_total,
    ensure_items_are_editable,
    recalculate_order_total,
)
from app.modules.services.use_cases.get_service_use_case import GetServiceUseCase


class AddServiceOrderItemUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        order_id: uuid.UUID,
        payload: AddServiceOrderItemRequest,
    ) -> ServiceOrderItemResponse:
        unit_price = payload.unit_price
        if payload.product_id is not None:
            product = await GetProductUseCase(connection_manager=self._connections).execute(
                tenant_id=tenant_id, database_name=database_name, product_id=payload.product_id
            )
            unit_price = unit_price if unit_price is not None else product.sale_price
        else:
            assert payload.service_id is not None  # garantido pelo schema
            service = await GetServiceUseCase(connection_manager=self._connections).execute(
                tenant_id=tenant_id, database_name=database_name, service_id=payload.service_id
            )
            unit_price = unit_price if unit_price is not None else service.price

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            order_repository = ServiceOrderRepository(session)
            order = await order_repository.get_by_id(order_id)
            if order is None:
                raise NotFoundError(
                    "Ordem de Serviço não encontrada.", code="SERVICE_ORDER_NOT_FOUND"
                )
            ensure_items_are_editable(order)

            item_repository = ServiceOrderItemRepository(session)
            item = ServiceOrderItem(
                service_order_id=order_id,
                product_id=payload.product_id,
                service_id=payload.service_id,
                quantity=payload.quantity,
                unit_price=unit_price,
                total=build_item_total(payload.quantity, unit_price),
            )
            await item_repository.create(item)
            new_total = await recalculate_order_total(session, order, item_repository)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SERVICE_ORDER_ITEM_ADDED",
                resource="service_orders",
                after={"item_id": str(item.id), "total": str(item.total), "order_total": str(new_total)},
            )
            await session.commit()

            return ServiceOrderItemResponse.model_validate(item)
