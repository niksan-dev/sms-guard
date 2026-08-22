"""add pincode to guards

Revision ID: b34806da148d
Revises: 33c8f9e1014b
Create Date: 2026-08-22 13:45:10.820227
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b34806da148d"
down_revision: Union[str, Sequence[str], None] = "33c8f9e1014b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    with op.batch_alter_table(
        "guards",
        schema=None
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "pincode",
                sa.String(length=6),
                nullable=True
            )
        )


def downgrade() -> None:

    with op.batch_alter_table(
        "guards",
        schema=None
    ) as batch_op:

        batch_op.drop_column(
            "pincode"
        )