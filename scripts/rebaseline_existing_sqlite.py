"""Rebaseline the existing local SQLite database.

Use this once for an existing development database after the migration
history has been replaced by the production baseline.

The script:
1. Creates a timestamped database backup.
2. Clears the obsolete Alembic revision marker.
3. Stamps the database at the new production baseline.
4. Runs the guard employment alignment migration.
5. Normalizes stored local file paths to POSIX separators.

It does not copy anything to PostgreSQL. That is a separate, controlled step.
"""

from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from alembic import command
from alembic.config import Config

from database.connection import BASE_DIR, DATABASE_URL


BASELINE_REVISION = "64c1dcdf57c3"


def _alembic_config() -> Config:
    config = Config(str(BASE_DIR / "alembic.ini"))
    config.set_main_option(
        "sqlalchemy.url",
        DATABASE_URL.replace("%", "%%"),
    )
    return config


def main() -> None:
    if not DATABASE_URL.startswith("sqlite"):
        raise RuntimeError(
            "This script is only for the local SQLite database. "
            "Set DATABASE_URL back to the local SQLite database before running it."
        )

    database_path = Path(DATABASE_URL.removeprefix("sqlite:///"))
    if not database_path.is_absolute():
        database_path = (BASE_DIR / database_path).resolve()

    if not database_path.exists():
        raise FileNotFoundError(f"SQLite database not found: {database_path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = database_path.with_name(
        f"{database_path.stem}_before_production_rebaseline_{timestamp}.db"
    )
    shutil.copy2(database_path, backup_path)
    print(f"Backup created: {backup_path}")

    import sqlite3

    connection = sqlite3.connect(database_path)
    try:
        connection.execute("DELETE FROM alembic_version")

        # Normalize paths written by Windows development environments. These
        # remain logical relative paths; persistent object storage is handled
        # by the next deployment step.
        for table, column in (
            ("company_settings", "logo_path"),
            ("guards", "photo_path"),
            ("guard_documents", "file_path"),
        ):
            connection.execute(
                f"UPDATE {table} SET {column} = REPLACE({column}, ?, ?) "
                f"WHERE {column} LIKE ?",
                ("\\", "/", "%\\%"),
            )

        connection.commit()
    finally:
        connection.close()

    config = _alembic_config()
    command.stamp(config, BASELINE_REVISION)
    command.upgrade(config, "head")

    print("Existing SQLite database successfully rebaselined.")
    print("Run 'alembic check' to verify the schema.")


if __name__ == "__main__":
    main()
