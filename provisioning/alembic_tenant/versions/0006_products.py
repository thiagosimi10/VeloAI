"""adiciona products

Revision ID: 0006_products
Revises: 0005_categories
Create Date: 2026-07-14

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0006_products"
down_revision: Union[str, None] = "0005_categories"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "category_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("categories.id"),
            nullable=True,
        ),
        sa.Column(
            "supplier_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("suppliers.id"),
            nullable=True,
        ),
        sa.Column("sku", sa.String(60), nullable=False, unique=True),
        sa.Column("barcode", sa.String(60), nullable=True, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("cost_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("sale_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("minimum_stock", sa.Integer(), nullable=True),
        sa.Column("maximum_stock", sa.Integer(), nullable=True),
        sa.Column("unit", sa.String(10), nullable=False, server_default="UN"),
        sa.Column("weight", sa.Numeric(10, 3), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("stock >= 0", name="ck_products_stock_non_negative"),
    )
    op.create_index("ix_products_name", "products", ["name"])
    op.create_index("ix_products_active", "products", ["active"])
    op.create_index("ix_products_category_id", "products", ["category_id"])
    op.create_index("ix_products_supplier_id", "products", ["supplier_id"])


def downgrade() -> None:
    op.drop_index("ix_products_supplier_id", table_name="products")
    op.drop_index("ix_products_category_id", table_name="products")
    op.drop_index("ix_products_active", table_name="products")
    op.drop_index("ix_products_name", table_name="products")
    op.drop_table("products")
