"""Acesso ao banco do tenant para Ordens de Serviço. Nenhuma regra de negócio aqui —
apenas persistência e consulta, conforme 00-AI-CONSTITUTION.md."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import ServiceOrder

from app.modules.service_orders.schemas.service_order import ServiceOrderFilterParams


class ServiceOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, order_id: uuid.UUID) -> ServiceOrder | None:
        result = await self._session.execute(
            select(ServiceOrder).where(
                ServiceOrder.id == order_id, ServiceOrder.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def count_all(self) -> int:
        """Conta TODOS os registros, incluindo os excluídos — usado para gerar o
        próximo `number` sequencial (único na tabela inteira)."""

        result = await self._session.execute(select(func.count()).select_from(ServiceOrder))
        return int(result.scalar_one())

    async def list(self, filters: ServiceOrderFilterParams) -> tuple[list[ServiceOrder], int]:
        conditions = [ServiceOrder.deleted_at.is_(None)]
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(ServiceOrder.number.ilike(pattern), ServiceOrder.problem.ilike(pattern))
            )
        if filters.customer_id is not None:
            conditions.append(ServiceOrder.customer_id == filters.customer_id)
        if filters.technician_id is not None:
            conditions.append(ServiceOrder.technician_id == filters.technician_id)
        if filters.status is not None:
            conditions.append(ServiceOrder.status == filters.status)

        count_result = await self._session.execute(
            select(func.count()).select_from(ServiceOrder).where(*conditions)
        )
        total = int(count_result.scalar_one())

        list_result = await self._session.execute(
            select(ServiceOrder)
            .where(*conditions)
            .order_by(ServiceOrder.opened_at.desc())
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
        )
        return list(list_result.scalars().all()), total

    async def create(self, order: ServiceOrder) -> ServiceOrder:
        self._session.add(order)
        await self._session.flush()
        return order

    async def update(self, order: ServiceOrder, data: dict[str, Any]) -> ServiceOrder:
        for field, value in data.items():
            setattr(order, field, value)
        await self._session.flush()
        return order

    async def soft_delete(self, order: ServiceOrder) -> None:
        order.deleted_at = datetime.now(UTC)
        await self._session.flush()

    async def commit(self) -> None:
        await self._session.commit()
