"""Align guard employment fields with the production model.

This migration is intentionally tolerant of the legacy SQLite schema that
still contains aadhaar_number/pincode and may already contain
 deactivation_date.  A fresh database created from the production baseline
already has the desired schema, so this migration becomes a no-op there.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "8b7f1f0c1d4a"
down_revision: Union[str, Sequence[str], None] = "64c1dcdf57c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _guard_columns() -> set[str]:
    bind = op.get_bind()
    return {
        column["name"]
        for column in inspect(bind).get_columns("guards")
    }


def upgrade() -> None:
    """Remove legacy identity fields and ensure deactivation_date exists."""

    columns = _guard_columns()
    dialect = op.get_bind().dialect.name

    # SQLite requires a table rebuild for safe multi-column changes.
    if dialect == "sqlite":
        if "aadhaar_number" in columns or "pincode" in columns or "deactivation_date" not in columns:
            with op.batch_alter_table(
                "guards",
                recreate="always",
                naming_convention={
                    "uq": "uq_%(table_name)s_%(column_0_name)s",
                },
            ) as batch_op:
                if "aadhaar_number" in columns:
                    batch_op.drop_column("aadhaar_number")
                if "pincode" in columns:
                    batch_op.drop_column("pincode")
                if "deactivation_date" not in columns:
                    batch_op.add_column(
                        sa.Column("deactivation_date", sa.Date(), nullable=True)
                    )
    else:
        if "deactivation_date" not in columns:
            op.add_column(
                "guards",
                sa.Column("deactivation_date", sa.Date(), nullable=True),
            )

        # These legacy fields are no longer part of the application model.
        columns = _guard_columns()
        if "aadhaar_number" in columns:
            op.drop_column("guards", "aadhaar_number")
        if "pincode" in columns:
            op.drop_column("guards", "pincode")

    # The current model indexes deactivation_date.
    indexes = {
        index["name"]: index
        for index in inspect(op.get_bind()).get_indexes("guards")
    }
    if "ix_guards_deactivation_date" not in indexes:
        op.create_index(
            "ix_guards_deactivation_date",
            "guards",
            ["deactivation_date"],
            unique=False,
        )


def downgrade() -> None:
    """Restore the old columns where practical.

    The old Aadhaar/pincode data is intentionally not recoverable from this
    migration because those fields were removed from the application model.
    Downgrade recreates the columns as nullable legacy fields only.
    """

    bind = op.get_bind()
    columns = _guard_columns()

    if "ix_guards_deactivation_date" in {
        index["name"] for index in inspect(bind).get_indexes("guards")
    }:
        op.drop_index("ix_guards_deactivation_date", table_name="guards")

    if bind.dialect.name == "sqlite":
        with op.batch_alter_table(
            "guards",
            recreate="always",
            naming_convention={
                "uq": "uq_%(table_name)s_%(column_0_name)s",
            },
        ) as batch_op:
            if "deactivation_date" in columns:
                batch_op.drop_column("deactivation_date")
            if "aadhaar_number" not in columns:
                batch_op.add_column(
                    sa.Column("aadhaar_number", sa.String(), nullable=True)
                )
            if "pincode" not in columns:
                batch_op.add_column(
                    sa.Column("pincode", sa.String(length=6), nullable=True)
                )
    else:
        if "deactivation_date" in columns:
            op.drop_column("guards", "deactivation_date")
        if "aadhaar_number" not in columns:
            op.add_column(
                "guards",
                sa.Column("aadhaar_number", sa.String(), nullable=True),
            )
        if "pincode" not in columns:
            op.add_column(
                "guards",
                sa.Column("pincode", sa.String(length=6), nullable=True),
            )
