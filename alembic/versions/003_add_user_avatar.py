"""add user avatar columns

Revision ID: 003_add_user_avatar
Revises: 002_create_feed_tables
Create Date: 2026-07-05

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_add_user_avatar"
down_revision: Union[str, None] = "002_create_feed_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("avatar_url", sa.String(length=512), nullable=True))
    op.add_column("users", sa.Column("avatar_public_id", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "avatar_public_id")
    op.drop_column("users", "avatar_url")
