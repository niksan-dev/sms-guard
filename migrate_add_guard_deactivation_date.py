"""
Add deactivation_date to guards.

Run once:
    python migrate_add_guard_deactivation_date.py

Creates a timestamped SQLite backup before changing the database.
"""

from pathlib import Path
from datetime import datetime
import shutil
import sqlite3

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "database.db"

# Adjust this only if your project uses a different SQLite file.
# If database.db does not exist, the script will report the path.
BACKUP_PATH = DB_PATH.with_name(
    f"{DB_PATH.stem}_backup_"
    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    f"{DB_PATH.suffix}"
)


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"SQLite database not found: {DB_PATH}"
        )

    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"Backup created: {BACKUP_PATH}")

    connection = sqlite3.connect(DB_PATH)

    try:
        columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(guards)"
            ).fetchall()
        }

        if "deactivation_date" in columns:
            print(
                "deactivation_date already exists. "
                "Nothing to change."
            )
            return

        connection.execute(
            "ALTER TABLE guards "
            "ADD COLUMN deactivation_date DATE"
        )

        connection.execute(
            "CREATE INDEX IF NOT EXISTS "
            "ix_guards_deactivation_date "
            "ON guards(deactivation_date)"
        )

        connection.commit()

        print(
            "Migration completed successfully. "
            "deactivation_date added to guards."
        )

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

