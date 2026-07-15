"""adiciona service_orders

Revision ID: 0009_service_orders
Revises: 0008_stock_movements
Create Date: 2026-07-14

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0009_service_orders"
down_revision: Union[str, None] = "0008_stock_movements"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "service_orders",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("number", sa.String(30), nullable=False, unique=True),
        sa.Column(
            "customer_id", sa.Uuid(as_uuid=True), sa.ForeignKey("customers.id"), nullable=False
        ),
        sa.Column(
            "technician_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id"), nullable=True
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("equipment", sa.String(200), nullable=True),
        sa.Column("serial_number", sa.String(100), nullable=True),
        sa.Column("problem", sa.Text(), nullable=True),
        sa.Column("diagnosis", sa.Text(), nullable=True),
        sa.Column("solution", sa.Text(), nullable=True),
        sa.Column("total", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column(
            "opened_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_service_orders_customer_id", "service_orders", ["customer_id"])
    op.create_index("ix_service_orders_technician_id", "service_orders", ["technician_id"])
    op.create_index("ix_service_orders_status", "service_orders", ["status"])


def downgrade() -> None:
    op.drop_index("ix_service_orders_status", table_name="service_orders")
    op.drop_index("ix_service_orders_technician_id", table_name="service_orders")
    op.drop_index("ix_service_orders_customer_id", table_name="service_orders")
    op.drop_table("service_orders")
