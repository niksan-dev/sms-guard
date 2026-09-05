"""Database initialization helper.

All environments use Alembic for schema creation and upgrades. This keeps
local SQLite and production PostgreSQL on the same migration path.
"""

from pathlib import Path

from alembic import command
from alembic.config import Config

from database.connection import DATABASE_URL


def init_db() -> None:
    """Create or upgrade the configured database to the current schema."""

    project_root = Path(__file__).resolve().parent.parent
    alembic_config = Config(str(project_root / "alembic.ini"))
    alembic_config.set_main_option(
        "sqlalchemy.url",
        DATABASE_URL.replace("%", "%%"),
    )

    command.upgrade(alembic_config, "head")
    print("Database schema is up to date.")


if __name__ == "__main__":
    init_db()
