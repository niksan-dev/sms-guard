from database.connection import Base, engine

# Import models so SQLAlchemy knows about them
from database.models import (
    User,
    Guard,
    Site,
    Shift,
    Attendance,
    Incident
)


def init_db():

    Base.metadata.create_all(
        bind=engine
    )

    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()