"""add monthly salary to guards

Revision ID: f09e1e5b039f
Revises: bd7c0457782e
Create Date: 2026-08-23 22:48:43.659082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f09e1e5b039f'
down_revision: Union[str, Sequence[str], None] = 'bd7c0457782e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    with op.batch_alter_table("guards") as batch_op:

        batch_op.add_column(
            sa.Column(
                "monthly_salary",
                sa.Float(),
                nullable=False,
                server_default="0"
            )
        )



def downgrade():

    with op.batch_alter_table("guards") as batch_op:

        batch_op.drop_column("monthly_salary")
