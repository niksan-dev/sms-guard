from database.connection import engine
from sqlalchemy import text


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS guard_work_logs (

    id INTEGER NOT NULL PRIMARY KEY,

    work_date DATE NOT NULL,

    guard_id INTEGER NOT NULL,

    site_id INTEGER NOT NULL,

    shift_number INTEGER NOT NULL,

    status VARCHAR NOT NULL DEFAULT 'Present',

    created_at DATETIME NOT NULL,

    updated_at DATETIME NOT NULL,

    CONSTRAINT uq_guard_date_shift
        UNIQUE (guard_id, work_date, shift_number),

    CONSTRAINT ck_guard_work_logs_shift_number
        CHECK (shift_number IN (1, 2)),

    FOREIGN KEY (guard_id)
        REFERENCES guards(id)
        ON DELETE CASCADE,

    FOREIGN KEY (site_id)
        REFERENCES sites(id)
        ON DELETE CASCADE
);
"""


CREATE_INDEXES_SQL = [
    """
    CREATE INDEX IF NOT EXISTS ix_guard_work_logs_work_date
    ON guard_work_logs (work_date);
    """,

    """
    CREATE INDEX IF NOT EXISTS ix_guard_work_logs_guard_id
    ON guard_work_logs (guard_id);
    """,

    """
    CREATE INDEX IF NOT EXISTS ix_guard_work_logs_site_id
    ON guard_work_logs (site_id);
    """
]


with engine.begin() as connection:

    # Create table
    connection.execute(
        text(CREATE_TABLE_SQL)
    )

    # Create indexes
    for sql in CREATE_INDEXES_SQL:

        connection.execute(
            text(sql)
        )


print("SUCCESS: guard_work_logs table created.")