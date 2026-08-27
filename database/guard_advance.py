from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Date,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from database.connection import Base


class GuardAdvance(Base):

    __tablename__ = "guard_advances"

    # ==============================================
    # PRIMARY KEY
    # ==============================================

    id = Column(
        Integer,
        primary_key=True,
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
    # CATEGORY
    #
    # Examples:
    # Uniform
    # Kharchi
    # Ration
    # Medical
    # Travel
    # Other
    # ==============================================

    category = Column(
        String(50),
        nullable=False,
        default="Other"
    )

    # ==============================================
    # AMOUNT
    # ==============================================

    amount = Column(
        Float,
        nullable=False,
        default=0.0
    )

    # ==============================================
    # DATE WHEN MONEY WAS GIVEN
    # ==============================================

    record_date = Column(
        Date,
        nullable=False,
        index=True
    )

    # ==============================================
    # DESCRIPTION / NOTES
    # ==============================================

    description = Column(
        String(500),
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
    # RELATIONSHIP
    # ==============================================

    guard = relationship(
        "Guard",
        back_populates="advances"
    )

    def __repr__(self):

        return (
            f"<GuardAdvance "
            f"id={self.id} "
            f"guard_id={self.guard_id} "
            f"amount={self.amount}>"
        )