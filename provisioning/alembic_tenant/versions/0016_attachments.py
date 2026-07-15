"""adiciona attachments

Revision ID: 0016_attachments
Revises: 0015_cash_flow
Create Date: 2026-07-17

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0016_attachments"
down_revision: Union[str, None] = "0015_cash_flow"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "attachments",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("resource_type", sa.String(30), nullable=False),
        sa.Column("resource_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False, unique=True),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column(
            "uploaded_by", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "ix_attachments_resource", "attachments", ["resource_type", "resource_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_attachments_resource", table_name="attachments")
    op.drop_table("attachments")
