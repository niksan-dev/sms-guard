from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database.connection import Base


class GuardDocument(Base):
    """Documents belonging to a security guard."""

    __tablename__ = "guard_documents"

    id = Column(Integer, primary_key=True, index=True)

    guard_id = Column(
        Integer,
        ForeignKey("guards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    document_type = Column(String(100), nullable=False)
    document_number = Column(String(100), nullable=True)
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)
    expiry_date = Column(Date, nullable=True)
    status = Column(String(30), nullable=False, default="Active")

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    guard = relationship(
        "Guard",
        back_populates="documents",
    )

    __table_args__ = (
        UniqueConstraint(
            "guard_id",
            "document_type",
            name="uq_guard_document_type",
        ),
    )
