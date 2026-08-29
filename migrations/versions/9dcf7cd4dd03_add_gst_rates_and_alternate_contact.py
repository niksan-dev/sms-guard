"""
add gst rates and alternate contact

Revision ID: 9dcf7cd4dd03
Revises: fb5f62c11167
Create Date: 2026-08-29 22:43:40.049501
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9dcf7cd4dd03"

down_revision: Union[
    str,
    Sequence[str],
    None
] = "fb5f62c11167"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add alternate contact and GST rates."""

    bind = op.get_bind()

    # ------------------------------------------------------
    # Check which columns already exist
    # ------------------------------------------------------

    columns = {
        row[1]
        for row in bind.execute(
            sa.text(
                "PRAGMA table_info(company_settings)"
            )
        )
    }

    # ------------------------------------------------------
    # Add alternate phone
    # ------------------------------------------------------

    if "alternate_phone" not in columns:

        op.execute(
            """
            ALTER TABLE company_settings
            ADD COLUMN alternate_phone VARCHAR(10)
            """
        )

    # ------------------------------------------------------
    # Add CGST
    #
    # IMPORTANT:
    # SQLite allows this because the column is nullable.
    # ------------------------------------------------------

    if "cgst_rate" not in columns:

        op.execute(
            """
            ALTER TABLE company_settings
            ADD COLUMN cgst_rate FLOAT
            """
        )

    # ------------------------------------------------------
    # Add SGST
    # ------------------------------------------------------

    if "sgst_rate" not in columns:

        op.execute(
            """
            ALTER TABLE company_settings
            ADD COLUMN sgst_rate FLOAT
            """
        )

    # ------------------------------------------------------
    # Set default rates for existing records
    # ------------------------------------------------------

    op.execute(
        """
        UPDATE company_settings
        SET cgst_rate = 9.0
        WHERE cgst_rate IS NULL
        """
    )

    op.execute(
        """
        UPDATE company_settings
        SET sgst_rate = 9.0
        WHERE sgst_rate IS NULL
        """
    )


def downgrade() -> None:

    with op.batch_alter_table(
        "company_settings",
        schema=None
    ) as batch_op:

        batch_op.drop_column("sgst_rate")
        batch_op.drop_column("cgst_rate")
        batch_op.drop_column("alternate_phone")