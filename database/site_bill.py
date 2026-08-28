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


class SiteBill(Base):

    __tablename__ = "site_bills"

    # ==================================================
    # PRIMARY KEY
    # ==================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ==================================================
    # BILL NUMBER
    # ==================================================

    bill_number = Column(
        String(100),
        unique=True,
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
    # BILLING PERIOD
    # ==================================================

    billing_month = Column(
        Integer,
        nullable=False,
        index=True
    )

    billing_year = Column(
        Integer,
        nullable=False,
        index=True
    )

    # ==================================================
    # BILL DATE
    # ==================================================

    bill_date = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # ==================================================
    # BILLING DETAILS
    # ==================================================

    total_days = Column(
        Integer,
        nullable=False
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
    # RATE
    # ==================================================

    monthly_rate = Column(
        Float,
        nullable=False,
        default=0.0
    )

    shift_rate = Column(
        Float,
        nullable=False,
        default=0.0
    )

    # ==================================================
    # AMOUNTS
    # ==================================================

    gross_amount = Column(
        Float,
        nullable=False,
        default=0.0
    )

    cgst_amount = Column(
        Float,
        nullable=False,
        default=0.0
    )

    sgst_amount = Column(
        Float,
        nullable=False,
        default=0.0
    )

    total_amount = Column(
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

    site = relationship(
        "Site",
        back_populates="site_bills"
    )