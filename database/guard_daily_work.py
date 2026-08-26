from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Date,
    DateTime,
    String,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
)

from sqlalchemy.orm import relationship

from database.connection import Base


class GuardDailyWork(Base):

    __tablename__ = "guard_daily_work"

    # ==================================================
    # PRIMARY KEY
    # ==================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ==================================================
    # WORK DATE
    # ==================================================

    work_date = Column(
        Date,
        nullable=False,
        index=True
    )

    # ==================================================
    # GUARD
    # ==================================================

    guard_id = Column(
        Integer,
        ForeignKey(
            "guards.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # ==================================================
    # SITE
    # ==================================================

    site_id = Column(
        Integer,
        ForeignKey(
            "sites.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # ==================================================
    # SHIFT
    #
    # 1 = Shift 1
    # 2 = Shift 2
    # ==================================================

    shift_number = Column(
        Integer,
        nullable=False
    )

    # ==================================================
    # ATTENDANCE STATUS
    # ==================================================

    status = Column(
        String(20),
        nullable=False,
        default="Present"
    )

    # ==================================================
    # RELATIONSHIPS
    # ==================================================

    guard = relationship(
        "Guard",
        back_populates="daily_work_records"
    )

    site = relationship(
        "Site",
        back_populates="daily_work_records"
    )

    # ==================================================
    # TIMESTAMPS
    # ==================================================

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # ==================================================
    # DATABASE CONSTRAINTS
    #
    # A guard cannot have the same shift twice
    # on the same date.
    #
    # This prevents:
    #
    # Rahul -> SITE-0001 -> Shift 1
    # Rahul -> SITE-0002 -> Shift 1  ❌
    #
    # But allows:
    #
    # Rahul -> SITE-0001 -> Shift 1
    # Rahul -> SITE-0002 -> Shift 2  ✅
    # ==================================================

    __table_args__ = (

        UniqueConstraint(
            "guard_id",
            "work_date",
            "shift_number",
            name="uq_guard_date_shift"
        ),

        CheckConstraint(
            "shift_number IN (1, 2)",
            name="ck_guard_daily_work_shift_number"
        ),

    )