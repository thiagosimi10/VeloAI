"""adiciona service_order_items

Revision ID: 0010_service_order_items
Revises: 0009_service_orders
Create Date: 2026-07-14

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0010_service_order_items"
down_revision: Union[str, None] = "0009_service_orders"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "service_order_items",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "service_order_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("service_orders.id"),
            nullable=False,
        ),
        sa.Column(
            "product_id", sa.Uuid(as_uuid=True), sa.ForeignKey("products.id"), nullable=True
        ),
        sa.Column(
            "service_id", sa.Uuid(as_uuid=True), sa.ForeignKey("services.id"), nullable=True
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("total", sa.Numeric(10, 2), nullable=False),
    )
    op.create_index(
        "ix_service_order_items_service_order_id", "service_order_items", ["service_order_id"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_service_order_items_service_order_id", table_name="service_order_items"
    )
    op.drop_table("service_order_items")
