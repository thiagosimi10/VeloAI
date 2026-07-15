"""Produtos do tenant, conforme 05-BANCO-DE-DADOS.md (tabela `products`). Esta fase
cobre apenas o cadastro central (preço, estoque atual, vínculo com Categoria e
Fornecedor) — campos fiscais, imagens, anexos e o histórico de movimentações de
estoque (tabela `stock_movements`, Fase 7 do Master Plan) ficam para uma iteração
futura."""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, TimestampMixin, UUIDPrimaryKeyMixin


class Product(TenantBase, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("stock >= 0", name="ck_products_stock_non_negative"),
    )

    category_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
    supplier_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("suppliers.id"), nullable=True
    )

    sku: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    barcode: Mapped[str | None] = mapped_column(String(60), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    cost_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    sale_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    stock: Mapped[int] = mapped_column(default=0, nullable=False)
    minimum_stock: Mapped[int | None] = mapped_column(nullable=True)
    maximum_stock: Mapped[int | None] = mapped_column(nullable=True)

    unit: Mapped[str] = mapped_column(String(10), default="UN", nullable=False)
    weight: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)

    active: Mapped[bool] = mapped_column(default=True, nullable=False)
