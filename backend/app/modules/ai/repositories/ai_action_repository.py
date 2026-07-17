"""Acesso ao banco do tenant para o registro de execução de Tools via MCP. Nenhuma
regra de negócio aqui — apenas persistência, conforme 00-AI-CONSTITUTION.md."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import AiAction


class AiActionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, action: AiAction) -> AiAction:
        self._session.add(action)
        await self._session.flush()
        return action
