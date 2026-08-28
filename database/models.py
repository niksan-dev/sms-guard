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
# USERS
# ==================================================

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    email = Column(
        String,
        unique=True,
        nullable=True,
        index=True
    )

    phone = Column(
        String,
        nullable=True
    )

    password_hash = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        nullable=False,
        index=True
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # One user -> one guard profile
    guard_profile = relationship(
        "Guard",
        back_populates="user",
        uselist=False
    )

    sites = relationship(
        "Site",
        back_populates="client",
        foreign_keys="Site.client_id"
    )

    auth_sessions = relationship(
        "AuthSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    

# ==================================================
# GUARDS
# ==================================================

class Guard(Base):

    __tablename__ = "guards"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=True
    )

    name = Column(
        String,
        nullable=False
    )

    employee_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    monthly_salary = Column(
        Float,
        nullable=False,
        default=0.0,
        server_default="0"
    )



    phone = Column(String, nullable=True)

    email = Column(String, nullable=True)

    aadhaar_number = Column(
        String,
        unique=True,
        nullable=True
    )

    address = Column(
        Text,
        nullable=True
    )

    # ADD THIS
    pincode = Column(
        String(6),
        nullable=True
    )

    emergency_contact = Column(
        String,
        nullable=True
    )

    photo_path = Column(
        String,
        nullable=True
    )

    joining_date = Column(
        Date,
        nullable=False
    )

    status = Column(
        String,
        default="Active",
        nullable=False
    )

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

    user = relationship(
        "User",
        back_populates="guard_profile"
    )

    shifts = relationship(
        "Shift",
        back_populates="guard"
    )

    attendance_records = relationship(
        "Attendance",
        back_populates="guard"
    )

    

    daily_work_records = relationship(
        "GuardDailyWork",
        back_populates="guard",
        cascade="all, delete-orphan"
    )

    advances = relationship(
        "GuardAdvance",
        back_populates="guard",
        cascade="all, delete-orphan"
    )

    site_assignments = relationship(
        "SiteGuardAssignment",
        back_populates="guard",
        cascade="all, delete-orphan"
    )

    salary_slips = relationship(
        "GuardSalarySlip",
        back_populates="guard",
        cascade="all, delete-orphan"
    )


# ==================================================
# SITE MODEL
# ==================================================

class Site(Base):

    __tablename__ = "sites"

    # ----------------------------------------------
    # PRIMARY KEY
    # ----------------------------------------------

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ----------------------------------------------
    # AUTO GENERATED SITE CODE
    # Example: SITE-0001
    # ----------------------------------------------

    site_code = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    # ----------------------------------------------
    # SITE INFORMATION
    # ----------------------------------------------

    name = Column(
        String,
        nullable=False
    )

    # ----------------------------------------------
    # CLIENT
    # ----------------------------------------------

    client_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    client = relationship(
        "User",
        back_populates="sites",
        foreign_keys=[client_id]
    )

    # ----------------------------------------------
    # CONTACT INFORMATION
    # ----------------------------------------------

    contact_person = Column(
        String,
        nullable=True
    )

    contact_phone = Column(
        String(10),
        nullable=True
    )

    email = Column(
        String,
        nullable=True
    )

    # ----------------------------------------------
    # ADDRESS
    # ----------------------------------------------

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

    # ----------------------------------------------
    # SECURITY REQUIREMENTS
    # ----------------------------------------------

    guards_required = Column(
        Integer,
        default=1,
        nullable=False
    )

    # Monthly rate charged per guard for this site
    guard_rate = Column(
        Float,
        default=0.0,
        nullable=False
    )

    # ----------------------------------------------
    # STATUS
    # ----------------------------------------------

    status = Column(
        String,
        default="Active",
        nullable=False
    )

    # ----------------------------------------------
    # CREATED DATE
    # ----------------------------------------------

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # ----------------------------------------------
    # RELATIONSHIPS
    # ----------------------------------------------

    shifts = relationship(
        "Shift",
        back_populates="site"
    )

    incidents = relationship(
        "Incident",
        back_populates="site"
    )

    payments = relationship(
        "Payment",
        back_populates="site"
    )
    guard_assignments = relationship(
        "SiteGuardAssignment",
        back_populates="site",
        cascade="all, delete-orphan"
    )

    daily_work_records = relationship(
        "GuardDailyWork",
        back_populates="site",
        cascade="all, delete-orphan"
    )

    site_bills = relationship(
        "SiteBill",
        back_populates="site",
        cascade="all, delete-orphan"
    )


# ==================================================
# SHIFTS
# ==================================================

class Shift(Base):

    __tablename__ = "shifts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    site_id = Column(
        Integer,
        ForeignKey("sites.id"),
        nullable=False
    )

    guard_id = Column(
        Integer,
        ForeignKey("guards.id"),
        nullable=False
    )

    start_time = Column(
        String,
        nullable=False
    )

    end_time = Column(
        String,
        nullable=False
    )

    date = Column(
        Date,
        nullable=False
    )

    guard = relationship(
        "Guard",
        back_populates="shifts"
    )

    site = relationship(
        "Site",
        back_populates="shifts"
    )


# ==================================================
# ATTENDANCE
# ==================================================

class Attendance(Base):

    __tablename__ = "attendance"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    guard_id = Column(
        Integer,
        ForeignKey("guards.id"),
        nullable=False
    )

    check_in = Column(
        DateTime,
        nullable=True
    )

    check_out = Column(
        DateTime,
        nullable=True
    )

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    guard = relationship(
        "Guard",
        back_populates="attendance_records"
    )


# ==================================================
# INCIDENTS
# ==================================================

class Incident(Base):

    __tablename__ = "incidents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    site_id = Column(
        Integer,
        ForeignKey("sites.id"),
        nullable=False
    )

    reported_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    status = Column(
        String,
        default="Open"
    )

    site = relationship(
        "Site",
        back_populates="incidents"
    )

    reporter = relationship(
        "User",
        foreign_keys=[reported_by]
    )

# ==================================================
# COMPANY SETTINGS MODELS & PAYMENT DETAILS
# ==================================================

from database.company_settings import CompanySettings

#===================================================
# PAYMENT MODEL
#===================================================
from database.payment import Payment

#=================================================
# SITE GUARD ASSIGNMENT MODEL
#=================================================
from database.site_guard_assignment import SiteGuardAssignment

#=================================================
# GUARD DAILY WORK MODEL
#=================================================
from database.guard_daily_work import GuardDailyWork

#=================================================
# GUARD ADVANCES
#=================================================
from database.guard_advance import GuardAdvance
#=================================================
# SITE BILLS
#=================================================
from database.site_bill import SiteBill

#=================================================
#GUARD SALARY SLIP
#=================================================
from database.guard_salary_slip import GuardSalarySlip
