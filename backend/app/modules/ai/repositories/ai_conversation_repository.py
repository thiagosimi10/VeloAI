"""Acesso ao banco do tenant para o registro de uso de IA. Nenhuma regra de negócio
aqui — apenas persistência e consulta, conforme 00-AI-CONSTITUTION.md."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import AiConversation


class AiConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, conversation: AiConversation) -> AiConversation:
        self._session.add(conversation)
        await self._session.flush()
        return conversation

    async def list_by_tenant(
        self, *, page: int, page_size: int
    ) -> tuple[list[AiConversation], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(AiConversation)
        )
        total = int(count_result.scalar_one())

        list_result = await self._session.execute(
            select(AiConversation)
            .order_by(AiConversation.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(list_result.scalars().all()), total
