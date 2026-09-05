"""Database connection and session management.

The application supports separate Development and Production databases.

Environment selection:
    ENVIRONMENT=development -> DATABASE_URL_DEV
    ENVIRONMENT=production  -> DATABASE_URL_PROD

Configuration can be supplied through environment variables or Streamlit
secrets.
"""

from __future__ import annotations
from dotenv import load_dotenv
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

# Load local .env when running locally.
# Render uses actual environment variables, so this has no effect there.
load_dotenv(BASE_DIR / ".env")
# ==================================================
# STREAMLIT SECRETS
# ==================================================

def _get_streamlit_secret(name: str) -> str | None:
    """Read a Streamlit secret without making Streamlit mandatory for CLI tools."""
    try:
        import streamlit as st

        value = st.secrets.get(name)

        if value:
            return str(value).strip()

    except Exception:
        # Alembic/CLI usage may run without an active Streamlit runtime.
        pass

    return None


# ==================================================
# ENVIRONMENT
# ==================================================

def get_environment() -> str:
    """Return the current application environment.

    Supported values:
        development
        production

    Defaults to development when not explicitly configured.
    """

    value = os.getenv("ENVIRONMENT", "").strip().lower()

    if not value:
        value = (
            _get_streamlit_secret("ENVIRONMENT")
            or "development"
        ).strip().lower()

    if value not in {"development", "production"}:
        raise RuntimeError(
            "Invalid ENVIRONMENT value. "
            "Expected 'development' or 'production'."
        )

    return value


ENVIRONMENT = get_environment()


# ==================================================
# DATABASE URL
# ==================================================

def _get_configured_database_url() -> str:
    """Return the database URL for the current environment.

    Development:
        DATABASE_URL_DEV

    Production:
        DATABASE_URL_PROD

    Environment variables take priority over Streamlit secrets.
    """

    if ENVIRONMENT == "production":
        variable_name = "DATABASE_URL_PROD"
    else:
        variable_name = "DATABASE_URL_DEV"

    # --------------------------------------------------
    # Environment variable
    # --------------------------------------------------

    value = os.getenv(variable_name, "").strip()

    # --------------------------------------------------
    # Streamlit secret
    # --------------------------------------------------

    if not value:
        value = _get_streamlit_secret(variable_name) or ""

    value = value.strip()

    if not value:
        raise RuntimeError(
            f"{variable_name} is not configured for "
            f"ENVIRONMENT={ENVIRONMENT}."
        )

    # --------------------------------------------------
    # Normalize PostgreSQL URLs
    # --------------------------------------------------

    if value.startswith("postgres://"):
        value = "postgresql://" + value[len("postgres://"):]

    return value


DATABASE_URL = _get_configured_database_url()


# ==================================================
# ENGINE
# ==================================================

_engine_kwargs = {
    "pool_pre_ping": True,
}

if DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {
        "check_same_thread": False
    }

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


# ==================================================
# DATABASE SESSION
# ==================================================

def get_db() -> Generator:
    """Yield a database session and always close it afterwards."""

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()