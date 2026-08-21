from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Text,
    Boolean
)

from datetime import datetime

from sqlalchemy.orm import relationship

from database.connection import Base


# ==================================================
# USERS
# ==================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        nullable=False,
        index=True
    )
    email = Column(
            String,
            unique=True,
            nullable=True
        )
    
    phone = Column(
        String,
        nullable=True
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    

# ==================================================
# GUARDS
# ==================================================

class Guard(Base):

    __tablename__ = "guards"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    name = Column(
        String,
        nullable=False
    )

    phone = Column(
        String,
        nullable=False
    )

    employee_id = Column(
        String,
        unique=True,
        nullable=False
    )

    joining_date = Column(
        Date,
        nullable=False
    )

    status = Column(
        String,
        default="Active"
    )

    # Relationships
    user = relationship(
        "User",
        backref="guard"
    )

    shifts = relationship(
        "Shift",
        back_populates="guard"
    )

    attendance_records = relationship(
        "Attendance",
        back_populates="guard"
    )


# ==================================================
# SITES
# ==================================================

class Site(Base):

    __tablename__ = "sites"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    address = Column(
        String,
        nullable=False
    )

    client_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    client = relationship(
        "User",
        foreign_keys=[client_id]
    )

    shifts = relationship(
        "Shift",
        back_populates="site"
    )

    incidents = relationship(
        "Incident",
        back_populates="site"
    )


# ==================================================
# SHIFTS
# ==================================================

class Shift(Base):

    __tablename__ = "shifts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    site_id = Column(
        Integer,
        ForeignKey("sites.id"),
        nullable=False
    )

    guard_id = Column(
        Integer,
        ForeignKey("guards.id"),
        nullable=False
    )

    start_time = Column(
        String,
        nullable=False
    )

    end_time = Column(
        String,
        nullable=False
    )

    date = Column(
        Date,
        nullable=False
    )

    site = relationship(
        "Site",
        back_populates="shifts"
    )

    guard = relationship(
        "Guard",
        back_populates="shifts"
    )


# ==================================================
# ATTENDANCE
# ==================================================

class Attendance(Base):

    __tablename__ = "attendance"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    guard_id = Column(
        Integer,
        ForeignKey("guards.id"),
        nullable=False
    )

    check_in = Column(
        DateTime,
        nullable=True
    )

    check_out = Column(
        DateTime,
        nullable=True
    )

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    guard = relationship(
        "Guard",
        back_populates="attendance_records"
    )


# ==================================================
# INCIDENTS
# ==================================================

class Incident(Base):

    __tablename__ = "incidents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    site_id = Column(
        Integer,
        ForeignKey("sites.id"),
        nullable=False
    )

    reported_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    status = Column(
        String,
        default="Open"
    )

    site = relationship(
        "Site",
        back_populates="incidents"
    )

    reporter = relationship(
        "User",
        foreign_keys=[reported_by]
    )