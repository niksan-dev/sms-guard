"""add guard daily work

Revision ID: aab1847554d5
Revises: a1a8282c1f82
Create Date: 2026-08-26 00:40:36.366566
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "aab1847554d5"
down_revision: Union[str, Sequence[str], None] = "a1a8282c1f82"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ==================================================
    # CREATE GUARD WORK LOGS TABLE
    # ==================================================

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

        # Shift 1 or Shift 2
        sa.Column(
            "shift_number",
            sa.Integer(),
            nullable=False
        ),

        # Present / Absent / etc.
        sa.Column(
            "status",
            sa.String(),
            nullable=False
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

        # Prevent duplicate shift entry
        sa.UniqueConstraint(
            "guard_id",
            "site_id",
            "work_date",
            "shift_number",
            name="uq_guard_site_date_shift"
        ),

        # Only Shift 1 or Shift 2 allowed
        sa.CheckConstraint(
            "shift_number IN (1, 2)",
            name="ck_guard_work_logs_shift_number"
        )
    )


    # ==================================================
    # CREATE INDEXES
    # ==================================================

    op.create_index(
        "ix_guard_work_logs_id",
        "guard_work_logs",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_guard_work_logs_guard_id",
        "guard_work_logs",
        ["guard_id"],
        unique=False
    )

    op.create_index(
        "ix_guard_work_logs_site_id",
        "guard_work_logs",
        ["site_id"],
        unique=False
    )

    op.create_index(
        "ix_guard_work_logs_work_date",
        "guard_work_logs",
        ["work_date"],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    # ==================================================
    # DROP INDEXES
    # ==================================================

    op.drop_index(
        "ix_guard_work_logs_work_date",
        table_name="guard_work_logs"
    )

    op.drop_index(
        "ix_guard_work_logs_site_id",
        table_name="guard_work_logs"
    )

    op.drop_index(
        "ix_guard_work_logs_guard_id",
        table_name="guard_work_logs"
    )

    op.drop_index(
        "ix_guard_work_logs_id",
        table_name="guard_work_logs"
    )


    # ==================================================
    # DROP TABLE
    # ==================================================

    op.drop_table(
        "guard_work_logs"
    )