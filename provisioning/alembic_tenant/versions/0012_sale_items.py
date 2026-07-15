"""adiciona sale_items

Revision ID: 0012_sale_items
Revises: 0011_sales
Create Date: 2026-07-15

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0012_sale_items"
down_revision: Union[str, None] = "0011_sales"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sale_items",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("sale_id", sa.Uuid(as_uuid=True), sa.ForeignKey("sales.id"), nullable=False),
        sa.Column(
            "product_id", sa.Uuid(as_uuid=True), sa.ForeignKey("products.id"), nullable=False
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
    )
    op.create_index("ix_sale_items_sale_id", "sale_items", ["sale_id"])


def downgrade() -> None:
    op.drop_index("ix_sale_items_sale_id", table_name="sale_items")
    op.drop_table("sale_items")
