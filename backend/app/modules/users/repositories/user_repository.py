"""Acesso ao banco do tenant para Usuários (somente leitura nesta fase). Nenhuma regra
de negócio aqui — apenas persistência e consulta, conforme 00-AI-CONSTITUTION.md."""

from __future__ import annotations

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import TenantUser

from app.modules.users.schemas.user import UserFilterParams


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: uuid.UUID) -> TenantUser | None:
        return await self._session.get(TenantUser, user_id)

    async def list(self, filters: UserFilterParams) -> tuple[list[TenantUser], int]:
        conditions = []
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(TenantUser.first_name.ilike(pattern), TenantUser.email.ilike(pattern))
            )

        count_result = await self._session.execute(
            select(func.count()).select_from(TenantUser).where(*conditions)
        )
        total = int(count_result.scalar_one())

        list_result = await self._session.execute(
            select(TenantUser)
            .where(*conditions)
            .order_by(TenantUser.first_name.asc())
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
        )
        return list(list_result.scalars().all()), total
