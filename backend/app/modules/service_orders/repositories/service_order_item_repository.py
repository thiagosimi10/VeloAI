"""Acesso ao banco do tenant para itens de Ordem de Serviço. Nenhuma regra de negócio
aqui — apenas persistência e consulta, conforme 00-AI-CONSTITUTION.md."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import ServiceOrderItem


class ServiceOrderItemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, item_id: uuid.UUID) -> ServiceOrderItem | None:
        return await self._session.get(ServiceOrderItem, item_id)

    async def list_all_by_order(self, service_order_id: uuid.UUID) -> list[ServiceOrderItem]:
        result = await self._session.execute(
            select(ServiceOrderItem).where(
                ServiceOrderItem.service_order_id == service_order_id
            )
        )
        return list(result.scalars().all())

    async def create(self, item: ServiceOrderItem) -> ServiceOrderItem:
        self._session.add(item)
        await self._session.flush()
        return item

    async def delete(self, item: ServiceOrderItem) -> None:
        await self._session.delete(item)
        await self._session.flush()
