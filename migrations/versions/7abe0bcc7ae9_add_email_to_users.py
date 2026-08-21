from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7abe0bcc7ae9"
down_revision: Union[str, Sequence[str], None] = "64eb85089b26"
branch_labels = None
depends_on = None


def upgrade() -> None:

    with op.batch_alter_table("users") as batch_op:

        batch_op.add_column(
            sa.Column(
                "email",
                sa.String(),
                nullable=True
            )
        )

        batch_op.create_unique_constraint(
            "uq_users_email",
            ["email"]
        )


def downgrade() -> None:

    with op.batch_alter_table("users") as batch_op:

        batch_op.drop_constraint(
            "uq_users_email",
            type_="unique"
        )

        batch_op.drop_column("email")