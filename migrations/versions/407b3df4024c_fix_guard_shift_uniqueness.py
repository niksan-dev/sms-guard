"""fix guard shift uniqueness

Revision ID: 407b3df4024c
Revises: aab1847554d5
Create Date: 2026-08-26 02:02:06.892404

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '407b3df4024c'
down_revision: Union[str, Sequence[str], None] = 'aab1847554d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
