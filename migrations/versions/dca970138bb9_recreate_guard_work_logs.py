"""recreate guard work logs

Revision ID: dca970138bb9
Revises: 407b3df4024c
Create Date: 2026-08-26 02:05:39.083439

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dca970138bb9"
down_revision: Union[str, Sequence[str], None] = "407b3df4024c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "guard_work_logs",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "work_date",
            sa.Date(),
            nullable=False
        ),

        sa.Column(
            "guard_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "site_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "shift_number",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="Present"
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False
        ),

        sa.ForeignKeyConstraint(
            ["guard_id"],
            ["guards.id"],
            ondelete="CASCADE"
        ),

        sa.ForeignKeyConstraint(
            ["site_id"],
            ["sites.id"],
            ondelete="CASCADE"
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),

        # ==================================================
        # IMPORTANT BUSINESS RULE
        #
        # One guard can work only ONE site
        # for the same date and same shift.
        # ==================================================

        sa.UniqueConstraint(
            "guard_id",
            "work_date",
            "shift_number",
            name="uq_guard_date_shift"
        ),

        # Only Shift 1 or Shift 2
        sa.CheckConstraint(
            "shift_number IN (1, 2)",
            name="ck_guard_work_logs_shift_number"
        )
    )

    # ==================================================
    # INDEXES
    # ==================================================

    op.create_index(
        "ix_guard_work_logs_id",
        "guard_work_logs",
        ["id"]
    )

    op.create_index(
        "ix_guard_work_logs_work_date",
        "guard_work_logs",
        ["work_date"]
    )

    op.create_index(
        "ix_guard_work_logs_guard_id",
        "guard_work_logs",
        ["guard_id"]
    )

    op.create_index(
        "ix_guard_work_logs_site_id",
        "guard_work_logs",
        ["site_id"]
    )


def downgrade() -> None:

    op.drop_index(
        "ix_guard_work_logs_site_id",
        table_name="guard_work_logs"
    )

    op.drop_index(
        "ix_guard_work_logs_guard_id",
        table_name="guard_work_logs"
    )

    op.drop_index(
        "ix_guard_work_logs_work_date",
        table_name="guard_work_logs"
    )

    op.drop_index(
        "ix_guard_work_logs_id",
        table_name="guard_work_logs"
    )

    op.drop_table(
        "guard_work_logs"
    )