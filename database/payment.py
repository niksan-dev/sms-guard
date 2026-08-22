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
# PAYMENTS / MONTHLY BILLING
# ==================================================

class Payment(Base):

    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ==============================================
    # INVOICE NUMBER
    # ==============================================

    invoice_number = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    # ==============================================
    # SITE / CLIENT
    # ==============================================

    site_id = Column(
        Integer,
        ForeignKey("sites.id"),
        nullable=False
    )

    client_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # ==============================================
    # BILLING PERIOD
    # ==============================================

    billing_month = Column(
        Date,
        nullable=False,
        index=True
    )

    billing_start_date = Column(
        Date,
        nullable=False
    )

    billing_end_date = Column(
        Date,
        nullable=False
    )

    due_date = Column(
        Date,
        nullable=True
    )

    # ==============================================
    # BILL TYPE
    # ==============================================

    # GST or Non-GST
    bill_type = Column(
        String,
        nullable=False,
        default="GST"
    )

    # ==============================================
    # AMOUNTS
    # ==============================================

    subtotal = Column(
        Float,
        nullable=False,
        default=0
    )

    gst_percentage = Column(
        Float,
        nullable=False,
        default=0
    )

    cgst_amount = Column(
        Float,
        nullable=False,
        default=0
    )

    sgst_amount = Column(
        Float,
        nullable=False,
        default=0
    )

    igst_amount = Column(
        Float,
        nullable=False,
        default=0
    )

    total_amount = Column(
        Float,
        nullable=False,
        default=0
    )

    # ==============================================
    # PAYMENT INFORMATION
    # ==============================================

    paid_amount = Column(
        Float,
        nullable=False,
        default=0
    )

    balance_amount = Column(
        Float,
        nullable=False,
        default=0
    )

    payment_status = Column(
        String,
        nullable=False,
        default="Pending"
    )
    # Pending
    # Partial
    # Paid
    # Overdue

    payment_date = Column(
        Date,
        nullable=True
    )

    payment_method = Column(
        String,
        nullable=True
    )

    payment_mode = Column(
        String,
        nullable=True
    )

    transaction_reference = Column(
        String,
        nullable=True
    )

    notes = Column(
        Text,
        nullable=True
    )

    remarks = Column(
        Text,
        nullable=True
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
    # RELATIONSHIPS
    # ==============================================

    site = relationship(
        "Site",
        back_populates="payments"
    )

    client = relationship(
        "User",
        foreign_keys=[client_id]
    )