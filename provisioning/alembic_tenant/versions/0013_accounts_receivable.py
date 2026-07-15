"""adiciona accounts_receivable

Revision ID: 0013_accounts_receivable
Revises: 0012_sale_items
Create Date: 2026-07-16

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0013_accounts_receivable"
down_revision: Union[str, None] = "0012_sale_items"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "accounts_receivable",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "customer_id", sa.Uuid(as_uuid=True), sa.ForeignKey("customers.id"), nullable=False
        ),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("payment_date", sa.Date(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_accounts_receivable_customer_id", "accounts_receivable", ["customer_id"]
    )
    op.create_index("ix_accounts_receivable_status", "accounts_receivable", ["status"])


def downgrade() -> None:
    op.drop_index("ix_accounts_receivable_status", table_name="accounts_receivable")
    op.drop_index("ix_accounts_receivable_customer_id", table_name="accounts_receivable")
    op.drop_table("accounts_receivable")
