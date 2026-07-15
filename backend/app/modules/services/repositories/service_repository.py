"""Acesso ao banco do tenant para Serviços. Nenhuma regra de negócio aqui — apenas
persistência e consulta, conforme 00-AI-CONSTITUTION.md."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import Service

from app.modules.services.schemas.service import ServiceFilterParams

_SORT_COLUMNS = {
    "name": Service.name,
    "code": Service.code,
    "created_at": Service.created_at,
}


class ServiceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, service_id: uuid.UUID) -> Service | None:
        result = await self._session.execute(
            select(Service).where(Service.id == service_id, Service.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def count_all(self) -> int:
        """Conta TODOS os registros, incluindo os excluídos (soft delete) — usado para
        gerar o próximo `code` sequencial. `code` é único na tabela inteira, então a
        contagem não pode ignorar linhas excluídas sob pena de gerar um valor
        duplicado."""

        result = await self._session.execute(select(func.count()).select_from(Service))
        return int(result.scalar_one())

    async def list(self, filters: ServiceFilterParams) -> tuple[list[Service], int]:
        conditions = [Service.deleted_at.is_(None)]
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(Service.name.ilike(pattern), Service.code.ilike(pattern))
            )
        if filters.category_id is not None:
            conditions.append(Service.category_id == filters.category_id)

        count_result = await self._session.execute(
            select(func.count()).select_from(Service).where(*conditions)
        )
        total = int(count_result.scalar_one())

        sort_column = _SORT_COLUMNS[filters.sort]
        order_by = sort_column.asc() if filters.order == "asc" else sort_column.desc()

        list_result = await self._session.execute(
            select(Service)
            .where(*conditions)
            .order_by(order_by)
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
        )
        return list(list_result.scalars().all()), total

    async def create(self, service: Service) -> Service:
        self._session.add(service)
        await self._session.flush()
        return service

    async def update(self, service: Service, data: dict[str, Any]) -> Service:
        for field, value in data.items():
            setattr(service, field, value)
        await self._session.flush()
        return service

    async def soft_delete(self, service: Service) -> None:
        service.deleted_at = datetime.now(UTC)
        service.active = False
        await self._session.flush()

    async def commit(self) -> None:
        await self._session.commit()
