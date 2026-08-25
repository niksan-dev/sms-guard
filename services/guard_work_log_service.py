from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from database.connection import SessionLocal
from database.guard_work_log import GuardWorkLog


# ==================================================
# CREATE GUARD WORK LOG
# ==================================================

def create_guard_work_log(
    guard_id,
    site_id,
    work_date,
    shift_number,
    status="Present"
):

    db = SessionLocal()

    try:

        # ------------------------------------------
        # VALIDATE SHIFT
        # ------------------------------------------

        shift_number = int(shift_number)

        if shift_number not in [1, 2]:

            return (
                False,
                "Shift number must be 1 or 2."
            )

        # ------------------------------------------
        # CHECK IF GUARD ALREADY WORKING SAME SHIFT
        #
        # IMPORTANT:
        # A guard cannot work Shift 1 at two sites
        # on the same date.
        #
        # A guard cannot work Shift 2 at two sites
        # on the same date.
        # ------------------------------------------

        existing_guard_shift = (
            db.query(GuardWorkLog)
            .filter(
                GuardWorkLog.guard_id == guard_id,
                GuardWorkLog.work_date == work_date,
                GuardWorkLog.shift_number == shift_number
            )
            .first()
        )

        if existing_guard_shift:

            return (
                False,
                f"This guard is already assigned to "
                f"Shift {shift_number} on this date."
            )

        # ------------------------------------------
        # CHECK SITE / SHIFT DUPLICATE
        #
        # Same guard + same site + same date + shift
        # ------------------------------------------

        existing_log = (
            db.query(GuardWorkLog)
            .filter(
                GuardWorkLog.guard_id == guard_id,
                GuardWorkLog.site_id == site_id,
                GuardWorkLog.work_date == work_date,
                GuardWorkLog.shift_number == shift_number
            )
            .first()
        )

        if existing_log:

            return (
                False,
                "This work record already exists."
            )

        # ------------------------------------------
        # CREATE LOG
        # ------------------------------------------

        work_log = GuardWorkLog(

            guard_id=guard_id,

            site_id=site_id,

            work_date=work_date,

            shift_number=shift_number,

            status=status or "Present"
        )

        db.add(work_log)

        db.commit()

        return (
            True,
            "Shift recorded successfully."
        )

    except IntegrityError as e:

        db.rollback()

        return (
            False,
            f"Unable to record shift: {str(e)}"
        )

    except Exception as e:

        db.rollback()

        return (
            False,
            f"Unable to record shift: {str(e)}"
        )

    finally:

        db.close()


# ==================================================
# GET WORK LOGS BY DATE
# ==================================================

def get_work_logs_by_date(work_date):

    db = SessionLocal()

    try:

        logs = (
            db.query(GuardWorkLog)
            .options(
                joinedload(GuardWorkLog.guard),
                joinedload(GuardWorkLog.site)
            )
            .filter(
                GuardWorkLog.work_date == work_date
            )
            .order_by(
                GuardWorkLog.shift_number.asc(),
                GuardWorkLog.id.desc()
            )
            .all()
        )

        return logs

    finally:

        db.close()


# ==================================================
# DELETE WORK LOG
# ==================================================

def delete_guard_work_log(log_id):

    db = SessionLocal()

    try:

        log = (
            db.query(GuardWorkLog)
            .filter(
                GuardWorkLog.id == log_id
            )
            .first()
        )

        if not log:

            return (
                False,
                "Work log not found."
            )

        db.delete(log)

        db.commit()

        return (
            True,
            "Work log deleted successfully."
        )

    except Exception as e:

        db.rollback()

        return (
            False,
            f"Unable to delete work log: {str(e)}"
        )

    finally:

        db.close()


# ==================================================
# GET DAILY WORK SUMMARY
# ==================================================

def get_daily_work_summary(work_date):

    db = SessionLocal()

    try:

        logs = (
            db.query(GuardWorkLog)
            .filter(
                GuardWorkLog.work_date == work_date
            )
            .all()
        )

        total_logs = len(logs)

        shift_1_count = sum(
            1
            for log in logs
            if log.shift_number == 1
        )

        shift_2_count = sum(
            1
            for log in logs
            if log.shift_number == 2
        )

        unique_guards = len(
            set(
                log.guard_id
                for log in logs
            )
        )

        unique_sites = len(
            set(
                log.site_id
                for log in logs
            )
        )

        return {

            "total_logs": total_logs,

            "shift_1_count": shift_1_count,

            "shift_2_count": shift_2_count,

            "unique_guards": unique_guards,

            "unique_sites": unique_sites
        }

    finally:

        db.close()

# ==================================================
# GUARD DAILY ATTENDANCE
# ==================================================

def get_guard_daily_attendance(work_date, site_id=None):

    db = SessionLocal()

    try:

        from database.models import Guard

        # Get all active guards
        guards = (
            db.query(Guard)
            .filter(
                Guard.status == "Active"
            )
            .order_by(
                Guard.name.asc()
            )
            .all()
        )

        attendance_data = []

        for guard in guards:

            query = (
                db.query(GuardWorkLog)
                .options(
                    joinedload(GuardWorkLog.site)
                )
                .filter(
                    GuardWorkLog.guard_id == guard.id,
                    GuardWorkLog.work_date == work_date
                )
            )

            # Optional site filter
            if site_id is not None:
                query = query.filter(
                    GuardWorkLog.site_id == site_id
                )

            logs = query.all()

            shift_1_log = next(
                (
                    log
                    for log in logs
                    if log.shift_number == 1
                ),
                None
            )

            shift_2_log = next(
                (
                    log
                    for log in logs
                    if log.shift_number == 2
                ),
                None
            )

            shift_1_present = shift_1_log is not None
            shift_2_present = shift_2_log is not None

            total_shifts = len(logs)

            # Get site names
            sites = list(
                dict.fromkeys(
                    [
                        f"{log.site.site_code} - {log.site.name}"
                        for log in logs
                        if log.site is not None
                    ]
                )
            )

            site_name = ", ".join(sites) if sites else "-"

            attendance_data.append({

                "guard_id": guard.id,

                "employee_id": guard.employee_id,

                "guard_name": guard.name,

                "site": site_name,

                "shift_1": shift_1_present,

                "shift_2": shift_2_present,

                "total_shifts": total_shifts,

                "status": (
                    "Present"
                    if total_shifts > 0
                    else "Absent"
                )
            })

        return attendance_data

    finally:

        db.close()


# ==================================================
# SITE DAILY ATTENDANCE
# ==================================================

def get_site_daily_attendance(work_date):

    db = SessionLocal()

    try:

        from database.models import Site

        sites = (
            db.query(Site)
            .filter(
                Site.status == "Active"
            )
            .order_by(
                Site.site_code.asc()
            )
            .all()
        )

        attendance_data = []

        for site in sites:

            logs = (
                db.query(GuardWorkLog)
                .filter(
                    GuardWorkLog.site_id == site.id,
                    GuardWorkLog.work_date == work_date
                )
                .all()
            )

            shift_1_count = sum(
                1
                for log in logs
                if log.shift_number == 1
            )

            shift_2_count = sum(
                1
                for log in logs
                if log.shift_number == 2
            )

            total_shifts = len(logs)

            guards_required = int(
                site.guards_required or 0
            )

            attendance_data.append({

                "site_id": site.id,

                "site_code": site.site_code,

                "site_name": site.name,

                "guards_required": guards_required,

                "shift_1_count": shift_1_count,

                "shift_2_count": shift_2_count,

                "total_shifts": total_shifts,

                "shift_1_required": guards_required,

                "shift_2_required": guards_required
            })

        return attendance_data

    finally:

        db.close()