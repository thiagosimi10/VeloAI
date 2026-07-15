"""Índice global de roteamento de login (e-mail → tenant), conforme o fluxo obrigatório
de 04-MULTI-TENANCY.md ("Login → Banco Master → Localiza Tenant → Obtém configuração →
Cria conexão SQLAlchemy").

Os dados completos do usuário (nome, senha, papel) vivem exclusivamente no banco do seu
tenant — esta tabela existe apenas para descobrir qual banco abrir a partir de um e-mail
informado no login. Nunca armazena senha ou qualquer dado além do necessário para o
roteamento."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.master.base import MasterBase, UUIDPrimaryKeyMixin


class TenantUserIndex(MasterBase, UUIDPrimaryKeyMixin):
    __tablename__ = "tenant_user_index"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
