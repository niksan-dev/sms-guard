from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context


# ==================================================
# PROJECT ROOT
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(
    0,
    BASE_DIR
)


# ==================================================
# IMPORT DATABASE MODELS
# ==================================================

from database.connection import Base

# Import models so Alembic can detect all tables
from database.models import (
    User,
    Guard,
    Site,
    Shift,
    Attendance,
    Incident
)


# ==================================================
# ALEMBIC CONFIG
# ==================================================

config = context.config


if config.config_file_name is not None:

    fileConfig(
        config.config_file_name
    )


# ==================================================
# DATABASE METADATA
# ==================================================

target_metadata = Base.metadata


# ==================================================
# DATABASE URL
# ==================================================

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "data",
    "security_guard.db"
)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL
)


# ==================================================
# OFFLINE MIGRATION
# ==================================================

def run_migrations_offline():

    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        }
    )

    with context.begin_transaction():

        context.run_migrations()


# ==================================================
# ONLINE MIGRATION
# ==================================================

def run_migrations_online():

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True
        )

        with context.begin_transaction():

            context.run_migrations()


# ==================================================
# RUN
# ==================================================

if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()