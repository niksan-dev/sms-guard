from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Float,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint
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
    # SHIFTS WORKED
    #
    # Allowed values:
    # 1 = One shift
    # 2 = Two shifts
    # ==================================================

    shifts_worked = Column(
        Integer,
        nullable=False,
        default=1
    )

    # ==================================================
    # FINANCIAL SNAPSHOT
    #
    # These values are copied when work is saved.
    #
    # Future changes to guard salary or site rate
    # will NOT affect old work records.
    # ==================================================

    monthly_salary = Column(
        Float,
        nullable=False,
        default=0.0
    )

    guard_rate = Column(
        Float,
        nullable=False,
        default=0.0
    )

    daily_salary = Column(
        Float,
        nullable=False,
        default=0.0
    )

    daily_revenue = Column(
        Float,
        nullable=False,
        default=0.0
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
    # CONSTRAINT
    #
    # One guard can have only one daily work record
    # for the same site on the same date.
    # ==================================================

    __table_args__ = (

        UniqueConstraint(
            "guard_id",
            "site_id",
            "work_date",
            name="uq_guard_site_daily_work"
        ),

    )