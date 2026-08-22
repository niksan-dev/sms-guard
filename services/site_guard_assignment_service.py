from datetime import date

from sqlalchemy.orm import joinedload

from database.connection import SessionLocal
from database.models import (
    Guard,
    Site
)

from database.site_guard_assignment import SiteGuardAssignment


# ==================================================
# ASSIGN GUARD TO SITE
# ==================================================

def assign_guard_to_site(
    guard_id,
    site_id,
    assigned_date=None
):

    db = SessionLocal()

    try:

        guard = (
            db.query(Guard)
            .filter(Guard.id == guard_id)
            .first()
        )

        if not guard:
            raise ValueError("Guard not found.")


        site = (
            db.query(Site)
            .filter(Site.id == site_id)
            .first()
        )

        if not site:
            raise ValueError("Site not found.")


        existing = (
            db.query(SiteGuardAssignment)
            .filter(
                SiteGuardAssignment.guard_id == guard_id,
                SiteGuardAssignment.site_id == site_id,
                SiteGuardAssignment.status == "Active"
            )
            .first()
        )

        if existing:
            raise ValueError(
                "This guard is already assigned to this site."
            )


        assignment = SiteGuardAssignment(
            guard_id=guard_id,
            site_id=site_id,
            assigned_date=assigned_date or date.today(),
            status="Active"
        )

        db.add(assignment)
        db.commit()
        db.refresh(assignment)

        return assignment

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


# ==================================================
# GET ACTIVE GUARDS FOR A SITE
# ==================================================

def get_site_guards(site_id):

    db = SessionLocal()

    try:

        return (
            db.query(SiteGuardAssignment)
            .options(
                joinedload(SiteGuardAssignment.guard)
            )
            .filter(
                SiteGuardAssignment.site_id == site_id,
                SiteGuardAssignment.status == "Active"
            )
            .order_by(
                SiteGuardAssignment.assigned_date.desc()
            )
            .all()
        )

    finally:

        db.close()


# ==================================================
# GET ACTIVE SITES FOR A GUARD
# ==================================================

def get_guard_sites(guard_id):

    db = SessionLocal()

    try:

        return (
            db.query(SiteGuardAssignment)
            .options(
                joinedload(SiteGuardAssignment.site)
            )
            .filter(
                SiteGuardAssignment.guard_id == guard_id,
                SiteGuardAssignment.status == "Active"
            )
            .order_by(
                SiteGuardAssignment.assigned_date.desc()
            )
            .all()
        )

    finally:

        db.close()


# ==================================================
# UNASSIGN
# ==================================================

def unassign_guard_from_site(
    assignment_id,
    unassigned_date=None
):

    db = SessionLocal()

    try:

        assignment = (
            db.query(SiteGuardAssignment)
            .filter(
                SiteGuardAssignment.id == assignment_id
            )
            .first()
        )

        if not assignment:
            raise ValueError("Assignment not found.")


        assignment.status = "Inactive"

        assignment.unassigned_date = (
            unassigned_date
            or date.today()
        )

        db.commit()

        return True

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()