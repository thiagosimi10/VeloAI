"""Fornecedores do tenant, conforme 05-BANCO-DE-DADOS.md (tabela `suppliers`, "Mesmo
padrão dos clientes"). Vínculo com Produtos, histórico de compras e contas a pagar
ficam para uma iteração futura."""

from __future__ import annotations

from sqlalchemy import CheckConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, TimestampMixin, UUIDPrimaryKeyMixin


class Supplier(TenantBase, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "suppliers"
    __table_args__ = (CheckConstraint("type IN ('PF', 'PJ')", name="ck_suppliers_type"),)

    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(2), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    document: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    state_registration: Mapped[str | None] = mapped_column(String(30), nullable=True)
    municipal_registration: Mapped[str | None] = mapped_column(String(30), nullable=True)

    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    mobile: Mapped[str | None] = mapped_column(String(30), nullable=True)
    whatsapp: Mapped[str | None] = mapped_column(String(30), nullable=True)

    zipcode: Mapped[str | None] = mapped_column(String(10), nullable=True)
    street: Mapped[str | None] = mapped_column(String(200), nullable=True)
    number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(2), nullable=True)
    country: Mapped[str] = mapped_column(String(60), default="Brasil", nullable=False)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
