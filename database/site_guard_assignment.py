from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Date,
    DateTime,
    String
)

from sqlalchemy.orm import relationship

from datetime import datetime

from database.connection import Base


class SiteGuardAssignment(Base):

    __tablename__ = "site_guard_assignments"


    # ==============================================
    # PRIMARY KEY
    # ==============================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    # ==============================================
    # SITE
    # ==============================================

    site_id = Column(
        Integer,
        ForeignKey("sites.id"),
        nullable=False,
        index=True
    )


    # ==============================================
    # GUARD
    # ==============================================

    guard_id = Column(
        Integer,
        ForeignKey("guards.id"),
        nullable=False,
        index=True
    )


    # ==============================================
    # ASSIGNMENT PERIOD
    # ==============================================

    assigned_date = Column(
        Date,
        default=datetime.utcnow().date,
        nullable=False
    )

    unassigned_date = Column(
        Date,
        nullable=True
    )


    # ==============================================
    # STATUS
    # ==============================================

    status = Column(
        String,
        default="Active",
        nullable=False
    )


    # ==============================================
    # CREATED
    # ==============================================

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


    # ==============================================
    # RELATIONSHIPS
    # ==============================================

    site = relationship(
        "Site",
        back_populates="guard_assignments"
    )

    guard = relationship(
        "Guard",
        back_populates="site_assignments"
    )