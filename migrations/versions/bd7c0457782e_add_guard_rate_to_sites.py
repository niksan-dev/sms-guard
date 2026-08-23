"""add guard rate to sites

Revision ID: bd7c0457782e
Revises: 2c7926edd11e
Create Date: 2026-08-23 19:33:30.443075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd7c0457782e'
down_revision: Union[str, Sequence[str], None] = '2c7926edd11e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():

    with op.batch_alter_table("sites") as batch_op:

        batch_op.add_column(
            sa.Column(
                "guard_rate",
                sa.Float(),
                nullable=False,
                server_default="0"
            )
        )


def downgrade():

    with op.batch_alter_table("sites") as batch_op:

        batch_op.drop_column("guard_rate")
