"""adiciona sales

Revision ID: 0011_sales
Revises: 0010_service_order_items
Create Date: 2026-07-15

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0011_sales"
down_revision: Union[str, None] = "0010_service_order_items"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sales",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "customer_id", sa.Uuid(as_uuid=True), sa.ForeignKey("customers.id"), nullable=False
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("payment_method", sa.String(30), nullable=True),
        sa.Column("discount", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("total", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_sales_customer_id", "sales", ["customer_id"])
    op.create_index("ix_sales_status", "sales", ["status"])


def downgrade() -> None:
    op.drop_index("ix_sales_status", table_name="sales")
    op.drop_index("ix_sales_customer_id", table_name="sales")
    op.drop_table("sales")
