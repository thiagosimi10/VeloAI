"""Catálogo global de papéis e permissões (fonte única de verdade), replicado para cada
tenant no momento do provisionamento — conforme 05-BANCO-DE-DADOS.md e
02-ARQUITETURA.md ("Permissões: RBAC. Perfis iniciais: Administrador...")."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.master.base import MasterBase, TimestampMixin, UUIDPrimaryKeyMixin


class Role(MasterBase, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Permission(MasterBase, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "permissions"

    module: Mapped[str] = mapped_column(String(80), nullable=False)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
