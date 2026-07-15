"""Conversas com IA do tenant, conforme 05-BANCO-DE-DADOS.md (tabela
`ai_conversations`) — registro de uso/consumo de cada chamada real ao AI Gateway
(Fase 13). Append-only, nunca atualizada nem apagada — mesmo padrão de
`StockMovement`/`CashFlowEntry`/`TenantAuditLog`: só `created_at` explícito, embora o
banco-fonte não liste esse campo — necessário para ordenar o histórico por mais
recente. `ai_actions` (execução de Tools via MCP) fica para a Fase 14, quando MCP
existir de verdade."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, UUIDPrimaryKeyMixin


class AiConversation(TenantBase, UUIDPrimaryKeyMixin):
    __tablename__ = "ai_conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    execution_time: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
