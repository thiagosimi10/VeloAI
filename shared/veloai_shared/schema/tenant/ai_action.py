"""Execução de Tools via MCP pelo assistente de IA, conforme 05-BANCO-DE-DADOS.md
(tabela `ai_actions`) — registro de auditoria de cada ação real que a IA executou no
sistema através de uma Tool (Fase 14). Append-only, nunca atualizada nem apagada —
mesmo padrão de `AiConversation`/`StockMovement`/`TenantAuditLog`: só `created_at`
explícito, embora o banco-fonte não liste esse campo — necessário para ordenar o
histórico por mais recente."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, UUIDPrimaryKeyMixin


class AiAction(TenantBase, UUIDPrimaryKeyMixin):
    __tablename__ = "ai_actions"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ai_conversations.id"), nullable=False
    )
    tool: Mapped[str] = mapped_column(String(100), nullable=False)
    service: Mapped[str] = mapped_column(String(100), nullable=False)
    execution: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
