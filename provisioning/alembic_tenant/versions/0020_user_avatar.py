"""adiciona avatar_key em users

Revision ID: 0020_user_avatar
Revises: 0019_knowledge_documents
Create Date: 2026-07-27

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0020_user_avatar"
down_revision: Union[str, None] = "0019_knowledge_documents"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("avatar_key", sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "avatar_key")
