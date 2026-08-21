from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


# Get project root directory
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# Database directory
DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

os.makedirs(
    DATA_DIR,
    exist_ok=True
)

# SQLite database path
DATABASE_PATH = os.path.join(
    DATA_DIR,
    "security_guard.db"
)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


# Database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for all models
Base = declarative_base()


def get_db():
    """
    Creates a database session.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()