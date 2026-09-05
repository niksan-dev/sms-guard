from logging.config import fileConfig
import os
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool


# ==================================================
# PROJECT ROOT
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, BASE_DIR)


# ==================================================
# IMPORT COMPLETE MODEL METADATA
# ==================================================

# database.models imports the application models and the newer standalone
# models (payments, bills, advances, documents, etc.). AuthSession is kept in
# its own module, so import it explicitly as well.
from database.connection import Base, DATABASE_URL  # noqa: E402
import database.models  # noqa: E402,F401
import database.auth_session  # noqa: E402,F401


# ==================================================
# ALEMBIC CONFIG
# ==================================================

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata

# The actual URL comes from the same configuration path as the application.
# Escape '%' for ConfigParser interpolation when setting it here.
config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL.replace("%", "%%"),
)


# ==================================================
# OFFLINE MIGRATION
# ==================================================

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ==================================================
# ONLINE MIGRATION
# ==================================================

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {},
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=connection.dialect.name == "sqlite",
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
