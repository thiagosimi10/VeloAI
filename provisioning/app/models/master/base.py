"""Base declarativa e mixins comuns do Banco Master, conforme 05-BANCO-DE-DADOS.md
("Toda tabela deverá possuir id, created_at, updated_at, deleted_at. Soft Delete
obrigatório. Sempre UUID.")."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from veloai_shared.security import new_uuid7


class MasterBase(DeclarativeBase):
    """Base declarativa para todas as tabelas do Banco Master."""


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid7)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
