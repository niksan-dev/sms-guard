from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime
)

from datetime import datetime

from database.connection import Base


class CompanySettings(Base):

    __tablename__ = "company_settings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ==============================================
    # COMPANY INFORMATION
    # ==============================================

    company_name = Column(
        String,
        nullable=False
    )

    owner_name = Column(
        String,
        nullable=True
    )

    phone = Column(
        String(10),
        nullable=True
    )

    email = Column(
        String,
        nullable=True
    )

    address = Column(
        Text,
        nullable=True
    )

    city = Column(
        String,
        nullable=True
    )

    state = Column(
        String,
        nullable=True
    )

    pincode = Column(
        String(6),
        nullable=True
    )

    # ==============================================
    # GST INFORMATION
    # ==============================================

    gst_number = Column(
        String(15),
        nullable=True
    )

    pan_number = Column(
        String(10),
        nullable=True
    )

    # ==============================================
    # BANK DETAILS
    # ==============================================

    bank_name = Column(
        String,
        nullable=True
    )

    account_holder_name = Column(
        String,
        nullable=True
    )

    account_number = Column(
        String,
        nullable=True
    )

    ifsc_code = Column(
        String,
        nullable=True
    )

    branch_name = Column(
        String,
        nullable=True
    )

    # ==============================================
    # INVOICE SETTINGS
    # ==============================================

    invoice_prefix = Column(
        String,
        default="INV",
        nullable=False
    )

    gst_invoice_prefix = Column(
        String,
        default="GST",
        nullable=False
    )

    # ==============================================
    # CREATED / UPDATED
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