"""adiciona ai_actions

Revision ID: 0018_ai_actions
Revises: 0017_ai_conversations
Create Date: 2026-07-15

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0018_ai_actions"
down_revision: Union[str, None] = "0017_ai_conversations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_actions",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("ai_conversations.id"),
            nullable=False,
        ),
        sa.Column("tool", sa.String(100), nullable=False),
        sa.Column("service", sa.String(100), nullable=False),
        sa.Column("execution", sa.JSON(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_ai_actions_conversation_id", "ai_actions", ["conversation_id"])


def downgrade() -> None:
    op.drop_index("ix_ai_actions_conversation_id", table_name="ai_actions")
    op.drop_table("ai_actions")
