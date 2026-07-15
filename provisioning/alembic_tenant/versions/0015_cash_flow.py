"""adiciona cash_flow

Revision ID: 0015_cash_flow
Revises: 0014_accounts_payable
Create Date: 2026-07-16

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0015_cash_flow"
down_revision: Union[str, None] = "0014_accounts_payable"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cash_flow",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("type", sa.String(10), nullable=False),
        sa.Column("category", sa.String(60), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "date", sa.Date(), server_default=sa.func.current_date(), nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_cash_flow_date", "cash_flow", ["date"])


def downgrade() -> None:
    op.drop_index("ix_cash_flow_date", table_name="cash_flow")
    op.drop_table("cash_flow")
