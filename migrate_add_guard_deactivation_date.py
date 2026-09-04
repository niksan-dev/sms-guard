"""Add guard deactivation date.

Run this once against the existing SQLite database after replacing
the application files.

This migration is intentionally idempotent.
"""

from pathlib import Path
import sqlite3
from datetime import datetime

from database.connection import DATABASE_URL


def get_sqlite_path():
    url = str(DATABASE_URL)
    if not url.startswith("sqlite:///"):
        raise RuntimeError(
            "This migration script currently supports SQLite only."
        )
    return Path(url.replace("sqlite:///", "", 1))


def migrate():
    db_path = get_sqlite_path()

    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    backup = db_path.with_name(
        f"{db_path.stem}_before_deactivation_"
        f"{datetime.now():%Y%m%d_%H%M%S}{db_path.suffix}"
    )
    backup.write_bytes(db_path.read_bytes())

    conn = sqlite3.connect(str(db_path))
    try:
        columns = {
            row[1]
            for row in conn.execute("PRAGMA table_info(guards)").fetchall()
        }

        if "deactivation_date" not in columns:
            conn.execute(
                "ALTER TABLE guards ADD COLUMN deactivation_date DATE"
            )

        conn.commit()
        print("Guard deactivation migration completed.")
        print(f"Backup created: {backup}")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
