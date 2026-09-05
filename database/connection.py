"""Database connection and session management.

The application supports both local SQLite development and a production
PostgreSQL database.  Production configuration is supplied through the
DATABASE_URL environment variable or Streamlit secrets.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# ==================================================
# PROJECT PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


# ==================================================
# DATABASE URL
# ==================================================

def _get_streamlit_secret(name: str) -> str | None:
    """Read a Streamlit secret without making Streamlit mandatory for tools."""
    try:
        import streamlit as st

        value = st.secrets.get(name)
        if value:
            return str(value).strip()
    except Exception:
        # Alembic/CLI usage may run without an active Streamlit runtime.
        pass

    return None


def get_database_url() -> str:
    """Return the configured database URL.

    Priority:
    1. DATABASE_URL environment variable
    2. Streamlit secret named DATABASE_URL
    3. Local SQLite database for development
    """

    value = os.getenv("DATABASE_URL", "").strip()

    if not value:
        value = _get_streamlit_secret("DATABASE_URL") or ""

    if value:
        # Some hosted providers expose postgres:// URLs. SQLAlchemy expects
        # postgresql://, so normalize the legacy scheme here.
        if value.startswith("postgres://"):
            value = "postgresql://" + value[len("postgres://") :]
        elif value.startswith("postgresql+psycopg2://"):
            # Keep existing explicit drivers untouched.
            pass

        return value

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{DATA_DIR / 'security_guard.db'}"


DATABASE_URL = get_database_url()


# ==================================================
# ENGINE
# ==================================================

_engine_kwargs = {
    "pool_pre_ping": True,
}

if DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    **_engine_kwargs,
)


# ==================================================
# SESSION
# ==================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ==================================================
# BASE
# ==================================================

Base = declarative_base()


def get_db() -> Generator:
    """Yield a database session and always close it afterwards."""

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
