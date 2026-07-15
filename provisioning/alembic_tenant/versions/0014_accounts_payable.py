"""adiciona accounts_payable

Revision ID: 0014_accounts_payable
Revises: 0013_accounts_receivable
Create Date: 2026-07-16

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0014_accounts_payable"
down_revision: Union[str, None] = "0013_accounts_receivable"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "accounts_payable",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "supplier_id", sa.Uuid(as_uuid=True), sa.ForeignKey("suppliers.id"), nullable=False
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
    op.create_index("ix_accounts_payable_supplier_id", "accounts_payable", ["supplier_id"])
    op.create_index("ix_accounts_payable_status", "accounts_payable", ["status"])


def downgrade() -> None:
    op.drop_index("ix_accounts_payable_status", table_name="accounts_payable")
    op.drop_index("ix_accounts_payable_supplier_id", table_name="accounts_payable")
    op.drop_table("accounts_payable")
