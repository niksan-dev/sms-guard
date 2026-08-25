from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint
)

from sqlalchemy.orm import relationship

from database.connection import Base


class GuardWorkLog(Base):

    __tablename__ = "guard_work_logs"


    # ==============================================
    # PRIMARY KEY
    # ==============================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    # ==============================================
    # WORK DATE
    # ==============================================

    work_date = Column(
        Date,
        nullable=False,
        index=True
    )


    # ==============================================
    # GUARD
    # ==============================================

    guard_id = Column(
        Integer,
        ForeignKey(
            "guards.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )


    # ==============================================
    # SITE
    # ==============================================

    site_id = Column(
        Integer,
        ForeignKey(
            "sites.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )


    # ==============================================
    # SHIFT
    #
    # 1 = Shift 1
    # 2 = Shift 2
    # ==============================================

    shift_number = Column(
        Integer,
        nullable=False
    )


    # ==============================================
    # STATUS
    # ==============================================

    status = Column(
        String,
        nullable=False,
        default="Present"
    )


    # ==============================================
    # RELATIONSHIPS
    # ==============================================

    guard = relationship(
        "Guard",
        back_populates="work_logs"
    )

    site = relationship(
        "Site",
        back_populates="work_logs"
    )


    # ==============================================
    # TIMESTAMPS
    # ==============================================

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


    # ==============================================
    # CONSTRAINTS
    # ==============================================

    __table_args__ = (

        # Same guard cannot have the same shift
        # at multiple sites on the same day.
        UniqueConstraint(
            "guard_id",
            "work_date",
            "shift_number",
            name="uq_guard_date_shift"
        ),

        CheckConstraint(
            "shift_number IN (1, 2)",
            name="ck_guard_work_logs_shift_number"
        ),

    )