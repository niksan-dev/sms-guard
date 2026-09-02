from pathlib import Path
from datetime import datetime
import shutil
import sqlite3

from alembic.migration import MigrationContext
from alembic.operations import Operations

from database.connection import SessionLocal


def main():
    db = SessionLocal()
    connection = db.get_bind()

    if connection.dialect.name != "sqlite":
        raise RuntimeError("This migration is intended for SQLite databases.")

    db_path = Path(connection.url.database).resolve()
    backup_path = db_path.with_name(
        f"{db_path.stem}_before_guard_aadhaar_pincode_removal_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}{db_path.suffix}"
    )

    db.close()

    if db_path.exists():
        shutil.copy2(db_path, backup_path)
        print(f"Database backup created: {backup_path}")

    raw = sqlite3.connect(str(db_path))
    try:
        raw.execute("PRAGMA foreign_keys=OFF")
        context = MigrationContext.configure(raw)
        operations = Operations(context)

        with operations.batch_alter_table(
            "guards",
            recreate="always",
            naming_convention={
                "uq": "uq_%(table_name)s_%(column_0_name)s"
            },
        ) as batch:
            # The old Aadhaar field was unique. SQLite cannot directly
            # DROP a UNIQUE column, so Alembic rebuilds the table.
            try:
                batch.drop_constraint(
                    "uq_guards_aadhaar_number",
                    type_="unique",
                )
            except Exception:
                pass

            batch.drop_column("aadhaar_number")

            # PIN Code is part of the guard's full address now.
            batch.drop_column("pincode")

        raw.commit()
        print("Successfully removed guards.aadhaar_number and guards.pincode.")
    except Exception:
        raw.rollback()
        raise
    finally:
        raw.execute("PRAGMA foreign_keys=ON")
        raw.close()


# if __name__ == "__main__":
#     main()
