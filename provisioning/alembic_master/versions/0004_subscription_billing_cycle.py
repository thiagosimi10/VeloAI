"""adiciona billing_cycle e asaas_checkout_id em subscriptions (checkout Asaas)

Revision ID: 0004_subscription_billing_cycle
Revises: 0003_platform_admin
Create Date: 2026-07-24

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0004_subscription_billing_cycle"
down_revision: Union[str, None] = "0003_platform_admin"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("subscriptions", sa.Column("billing_cycle", sa.String(20), nullable=True))
    op.add_column("subscriptions", sa.Column("asaas_checkout_id", sa.String(60), nullable=True))


def downgrade() -> None:
    op.drop_column("subscriptions", "asaas_checkout_id")
    op.drop_column("subscriptions", "billing_cycle")
