"""adiciona services

Revision ID: 0007_services
Revises: 0006_products
Create Date: 2026-07-14

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0007_services"
down_revision: Union[str, None] = "0006_products"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "services",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "category_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("categories.id"),
            nullable=True,
        ),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("estimated_time", sa.Integer(), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_services_name", "services", ["name"])
    op.create_index("ix_services_active", "services", ["active"])
    op.create_index("ix_services_category_id", "services", ["category_id"])


def downgrade() -> None:
    op.drop_index("ix_services_category_id", table_name="services")
    op.drop_index("ix_services_active", table_name="services")
    op.drop_index("ix_services_name", table_name="services")
    op.drop_table("services")
