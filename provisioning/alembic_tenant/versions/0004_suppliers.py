"""adiciona suppliers

Revision ID: 0004_suppliers
Revises: 0003_customers
Create Date: 2026-07-14

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0004_suppliers"
down_revision: Union[str, None] = "0003_customers"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "suppliers",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("type", sa.String(2), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("document", sa.String(20), nullable=False, unique=True),
        sa.Column("state_registration", sa.String(30), nullable=True),
        sa.Column("municipal_registration", sa.String(30), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("mobile", sa.String(30), nullable=True),
        sa.Column("whatsapp", sa.String(30), nullable=True),
        sa.Column("zipcode", sa.String(10), nullable=True),
        sa.Column("street", sa.String(200), nullable=True),
        sa.Column("number", sa.String(20), nullable=True),
        sa.Column("district", sa.String(100), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(2), nullable=True),
        sa.Column("country", sa.String(60), nullable=False, server_default="Brasil"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("type IN ('PF', 'PJ')", name="ck_suppliers_type"),
    )
    op.create_index("ix_suppliers_name", "suppliers", ["name"])
    op.create_index("ix_suppliers_active", "suppliers", ["active"])


def downgrade() -> None:
    op.drop_index("ix_suppliers_active", table_name="suppliers")
    op.drop_index("ix_suppliers_name", table_name="suppliers")
    op.drop_table("suppliers")
