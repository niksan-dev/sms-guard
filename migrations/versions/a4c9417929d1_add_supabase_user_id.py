"""add supabase user id

Revision ID: a4c9417929d1
Revises: 64c1dcdf57c3
Create Date: 2026-09-12 00:36:41.748161

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a4c9417929d1"

down_revision: Union[str, Sequence[str], None] = "64c1dcdf57c3"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "users",
        sa.Column(
            "supabase_user_id",
            sa.String(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_users_supabase_user_id",
        "users",
        ["supabase_user_id"],
        unique=True,
    )


def downgrade() -> None:

    op.drop_index(
        "ix_users_supabase_user_id",
        table_name="users",
    )

    op.drop_column(
        "users",
        "supabase_user_id",
    )