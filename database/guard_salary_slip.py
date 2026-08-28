from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
    Text,
)

from sqlalchemy.orm import relationship

from database.connection import Base


class GuardSalarySlip(Base):

    __tablename__ = "guard_salary_slips"

    # ==================================================
    # PRIMARY KEY
    # ==================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ==================================================
    # SLIP NUMBER
    # ==================================================

    slip_number = Column(
        String(100),
        unique=True,
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
    # SALARY PERIOD
    # ==================================================

    salary_month = Column(
        Integer,
        nullable=False,
        index=True
    )

    salary_year = Column(
        Integer,
        nullable=False,
        index=True
    )

    # ==================================================
    # SLIP DATE
    # ==================================================

    slip_date = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # ==================================================
    # ATTENDANCE
    # ==================================================

    total_days = Column(
        Integer,
        nullable=False
    )

    present_days = Column(
        Integer,
        nullable=False,
        default=0
    )

    shift_1_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    shift_2_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    total_shifts = Column(
        Integer,
        nullable=False,
        default=0
    )

    # ==================================================
    # SALARY
    # ==================================================

    monthly_salary = Column(
        Float,
        nullable=False,
        default=0.0
    )

    shift_rate = Column(
        Float,
        nullable=False,
        default=0.0
    )

    gross_salary = Column(
        Float,
        nullable=False,
        default=0.0
    )

    # ==================================================
    # ADVANCES
    # ==================================================

    total_advance = Column(
        Float,
        nullable=False,
        default=0.0
    )

    # ==================================================
    # NET PAYABLE
    # ==================================================

    net_payable = Column(
        Float,
        nullable=False,
        default=0.0
    )

    # ==================================================
    # PDF
    # ==================================================

    pdf_data = Column(
        Text,
        nullable=True
    )

    # ==================================================
    # STATUS
    # ==================================================

    status = Column(
        String(20),
        nullable=False,
        default="Generated"
    )

    # ==================================================
    # TIMESTAMPS
    # ==================================================

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ==================================================
    # RELATIONSHIP
    # ==================================================

    guard = relationship(
        "Guard",
        back_populates="salary_slips"
    )