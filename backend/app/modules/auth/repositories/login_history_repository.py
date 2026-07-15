"""Registro de tentativas de login, conforme 29-SECURITY.md ("Login: Registro de
tentativas.")."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import LoginHistory


class LoginHistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(
        self,
        *,
        user_id: uuid.UUID | None,
        email: str,
        success: bool,
        ip: str | None,
        user_agent: str | None,
    ) -> LoginHistory:
        entry = LoginHistory(
            user_id=user_id, email=email, success=success, ip=ip, user_agent=user_agent
        )
        self._session.add(entry)
        await self._session.flush()
        return entry
