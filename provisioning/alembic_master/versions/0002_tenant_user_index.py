"""adiciona tenant_user_index (roteamento de login)

Revision ID: 0002_tenant_user_index
Revises: 0001_initial
Create Date: 2026-07-14

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0002_tenant_user_index"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant_user_index",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_tenant_user_index_tenant_id", "tenant_user_index", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_tenant_user_index_tenant_id", table_name="tenant_user_index")
    op.drop_table("tenant_user_index")
