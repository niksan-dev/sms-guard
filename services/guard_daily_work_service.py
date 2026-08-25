from calendar import monthrange

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from database.connection import SessionLocal
from database.guard_daily_work import GuardDailyWork
from database.guard_work_log import GuardWorkLog
from database.models import Guard, Site


# ==================================================
# HELPER
# ==================================================

def get_days_in_month(work_date):
    """
    Return the actual number of days in the month.

    Examples:
    January  -> 31
    February -> 28 / 29
    April    -> 30
    """

    return monthrange(
        work_date.year,
        work_date.month
    )[1]


# ==================================================
# SAVE / UPDATE GUARD DAILY WORK
# ==================================================

def save_guard_daily_work(
    work_date,
    guard_id,
    site_id,
    shifts_worked=None
):
    """
    Create or update the financial daily work record.

    shifts_worked is optional.
    The actual number of Present shifts is always
    calculated from GuardWorkLog.
    """

    db = SessionLocal()

    try:

        # ==========================================
        # GET GUARD
        # ==========================================

        guard = (
            db.query(Guard)
            .filter(
                Guard.id == guard_id
            )
            .first()
        )

        if not guard:
            return False, "Guard not found."


        # ==========================================
        # GET SITE
        # ==========================================

        site = (
            db.query(Site)
            .filter(
                Site.id == site_id
            )
            .first()
        )

        if not site:
            return False, "Site not found."


        # ==========================================
        # CALCULATE ACTUAL PRESENT SHIFTS
        # FROM GUARD WORK LOGS
        # ==========================================

        actual_shifts_worked = (
            db.query(GuardWorkLog)
            .filter(
                GuardWorkLog.work_date == work_date,
                GuardWorkLog.guard_id == guard_id,
                GuardWorkLog.site_id == site_id,
                GuardWorkLog.status == "Present"
            )
            .count()
        )

        # Maximum allowed shifts per guard per day
        actual_shifts_worked = min(
            actual_shifts_worked,
            2
        )

        if actual_shifts_worked <= 0:
            return (
                False,
                "No present shifts found for this guard and site."
            )


        # ==========================================
        # ACTUAL DAYS IN CURRENT MONTH
        # ==========================================

        days_in_month = get_days_in_month(
            work_date
        )


        # ==========================================
        # FINANCIAL VALUES
        # ==========================================

        monthly_salary = float(
            guard.monthly_salary or 0.0
        )

        monthly_rate = float(
            site.guard_rate or 0.0
        )


        # ==========================================
        # CALCULATE FINANCIAL AMOUNTS
        #
        # 1 Shift = Monthly Amount / Days In Month
        # 2 Shifts = 2 × Monthly Amount / Days In Month
        # ==========================================

        salary_per_shift = (
            monthly_salary / days_in_month
        )

        revenue_per_shift = (
            monthly_rate / days_in_month
        )

        daily_salary = (
            salary_per_shift
            * actual_shifts_worked
        )

        daily_revenue = (
            revenue_per_shift
            * actual_shifts_worked
        )


        # ==========================================
        # FIND EXISTING DAILY WORK RECORD
        # ==========================================

        daily_work = (
            db.query(GuardDailyWork)
            .filter(
                GuardDailyWork.work_date == work_date,
                GuardDailyWork.guard_id == guard_id,
                GuardDailyWork.site_id == site_id
            )
            .first()
        )


        # ==========================================
        # UPDATE EXISTING RECORD
        # ==========================================

        if daily_work:

            daily_work.shifts_worked = (
                actual_shifts_worked
            )

            daily_work.monthly_salary = (
                monthly_salary
            )

            daily_work.guard_rate = (
                monthly_rate
            )

            daily_work.daily_salary = (
                daily_salary
            )

            daily_work.daily_revenue = (
                daily_revenue
            )

            db.commit()

            return (
                True,
                "Daily work updated successfully."
            )


        # ==========================================
        # CREATE NEW RECORD
        # ==========================================

        daily_work = GuardDailyWork(

            work_date=work_date,

            guard_id=guard_id,

            site_id=site_id,

            shifts_worked=actual_shifts_worked,

            monthly_salary=monthly_salary,

            guard_rate=monthly_rate,

            daily_salary=daily_salary,

            daily_revenue=daily_revenue
        )

        db.add(
            daily_work
        )

        db.commit()

        return (
            True,
            "Daily work saved successfully."
        )


    except Exception as e:

        db.rollback()

        return (
            False,
            f"Unable to save daily work: {str(e)}"
        )


    finally:

        db.close()


# ==================================================
# DELETE DAILY WORK
# ==================================================

def delete_daily_work(
    work_date,
    guard_id,
    site_id
):

    db = SessionLocal()

    try:

        record = (
            db.query(GuardDailyWork)
            .filter(
                GuardDailyWork.work_date == work_date,
                GuardDailyWork.guard_id == guard_id,
                GuardDailyWork.site_id == site_id
            )
            .first()
        )

        if not record:

            return (
                False,
                "Daily work record not found."
            )


        db.delete(
            record
        )

        db.commit()

        return (
            True,
            "Daily work record deleted successfully."
        )


    except Exception as e:

        db.rollback()

        return (
            False,
            str(e)
        )


    finally:

        db.close()


# ==================================================
# GET DAILY WORK RECORDS
# ==================================================

def get_daily_work_records(
    work_date=None
):

    db = SessionLocal()

    try:

        query = (
            db.query(GuardDailyWork)
            .options(
                joinedload(
                    GuardDailyWork.guard
                ),
                joinedload(
                    GuardDailyWork.site
                )
            )
        )


        if work_date:

            query = query.filter(
                GuardDailyWork.work_date == work_date
            )


        records = (
            query
            .order_by(
                GuardDailyWork.work_date.desc(),
                GuardDailyWork.id.desc()
            )
            .all()
        )


        return records


    except Exception as e:

        print(
            f"Unable to load daily work records: {e}"
        )

        return []


    finally:

        db.close()


# ==================================================
# GET DAILY WORK SUMMARY
#
# SOURCE OF TRUTH:
# GuardWorkLog
#
# This ensures the summary immediately reflects
# recorded shifts even before a GuardDailyWork
# financial record exists.
# ==================================================

def get_daily_work_summary(
    work_date
):

    db = SessionLocal()

    try:

        # ==========================================
        # GET ALL PRESENT WORK LOGS
        # ==========================================

        logs = (
            db.query(GuardWorkLog)
            .options(
                joinedload(
                    GuardWorkLog.guard
                ),
                joinedload(
                    GuardWorkLog.site
                )
            )
            .filter(
                GuardWorkLog.work_date == work_date,
                GuardWorkLog.status == "Present"
            )
            .all()
        )


        # ==========================================
        # TOTAL UNIQUE GUARDS
        # ==========================================

        unique_guard_ids = {
            log.guard_id
            for log in logs
        }


        # ==========================================
        # TOTAL UNIQUE SITES
        # ==========================================

        unique_site_ids = {
            log.site_id
            for log in logs
        }


        # ==========================================
        # TOTAL SHIFTS
        # ==========================================

        total_shifts = len(
            logs
        )


        # ==========================================
        # ACTUAL DAYS IN MONTH
        # ==========================================

        days_in_month = get_days_in_month(
            work_date
        )


        total_salary = 0.0
        total_revenue = 0.0


        # ==========================================
        # CALCULATE EACH SHIFT FINANCIAL VALUE
        # ==========================================

        for log in logs:

            if log.guard:

                monthly_salary = float(
                    log.guard.monthly_salary or 0.0
                )

                total_salary += (
                    monthly_salary
                    / days_in_month
                )


            if log.site:

                monthly_rate = float(
                    log.site.guard_rate or 0.0
                )

                total_revenue += (
                    monthly_rate
                    / days_in_month
                )


        return {

            "total_records": len(
                unique_guard_ids
            ),

            "total_guards": len(
                unique_guard_ids
            ),

            "total_shifts": total_shifts,

            "sites_covered": len(
                unique_site_ids
            ),

            "total_salary": total_salary,

            "total_revenue": total_revenue,

            "profit": (
                total_revenue
                - total_salary
            )
        }


    except Exception as e:

        print(
            f"Unable to load daily work summary: {e}"
        )

        return {

            "total_records": 0,

            "total_guards": 0,

            "total_shifts": 0,

            "sites_covered": 0,

            "total_salary": 0.0,

            "total_revenue": 0.0,

            "profit": 0.0
        }


    finally:

        db.close()


# ==================================================
# GUARD DAILY ATTENDANCE
#
# SOURCE OF TRUTH:
# GuardWorkLog
# ==================================================

def get_guard_daily_attendance(
    work_date,
    site_id=None,
    guard_id=None
):

    db = SessionLocal()

    try:

        # ==========================================
        # GET ALL ACTIVE GUARDS
        # ==========================================

        guards_query = (
            db.query(Guard)
            .filter(
                func.lower(
                    func.coalesce(
                        Guard.status,
                        ""
                    )
                ) == "active"
            )
        )


        if guard_id is not None:

            guards_query = guards_query.filter(
                Guard.id == guard_id
            )


        guards = (
            guards_query
            .order_by(
                Guard.name.asc()
            )
            .all()
        )


        # ==========================================
        # GET PRESENT SHIFT LOGS
        # ==========================================

        logs_query = (
            db.query(GuardWorkLog)
            .options(
                joinedload(
                    GuardWorkLog.guard
                ),
                joinedload(
                    GuardWorkLog.site
                )
            )
            .filter(
                GuardWorkLog.work_date == work_date,
                GuardWorkLog.status == "Present"
            )
        )


        if site_id is not None:

            logs_query = logs_query.filter(
                GuardWorkLog.site_id == site_id
            )


        if guard_id is not None:

            logs_query = logs_query.filter(
                GuardWorkLog.guard_id == guard_id
            )


        logs = logs_query.all()


        # ==========================================
        # CREATE ATTENDANCE MAP
        #
        # One guard can only have:
        # Shift 1 = one site
        # Shift 2 = one site
        # ==========================================

        attendance_map = {}


        for log in logs:

            if log.guard_id not in attendance_map:

                attendance_map[
                    log.guard_id
                ] = {

                    "shift_1": None,

                    "shift_2": None
                }


            if log.shift_number == 1:

                attendance_map[
                    log.guard_id
                ]["shift_1"] = log


            elif log.shift_number == 2:

                attendance_map[
                    log.guard_id
                ]["shift_2"] = log


        # ==========================================
        # BUILD GUARD ATTENDANCE DATA
        # ==========================================

        attendance_data = []


        for guard in guards:

            guard_attendance = attendance_map.get(
                guard.id,
                {
                    "shift_1": None,
                    "shift_2": None
                }
            )


            shift_1_log = (
                guard_attendance["shift_1"]
            )

            shift_2_log = (
                guard_attendance["shift_2"]
            )


            # ======================================
            # SHIFT 1
            # ======================================

            if shift_1_log:

                shift_1_status = "Present"

                shift_1_site = (
                    f"{shift_1_log.site.site_code} - "
                    f"{shift_1_log.site.name}"
                    if shift_1_log.site
                    else "Unknown"
                )

            else:

                shift_1_status = "Absent"

                shift_1_site = "-"


            # ======================================
            # SHIFT 2
            # ======================================

            if shift_2_log:

                shift_2_status = "Present"

                shift_2_site = (
                    f"{shift_2_log.site.site_code} - "
                    f"{shift_2_log.site.name}"
                    if shift_2_log.site
                    else "Unknown"
                )

            else:

                shift_2_status = "Absent"

                shift_2_site = "-"


            # ======================================
            # TOTAL SHIFTS
            # ======================================

            shifts_worked = 0


            if shift_1_log:
                shifts_worked += 1


            if shift_2_log:
                shifts_worked += 1


            # ======================================
            # ATTENDANCE STATUS
            # ======================================

            attendance_status = (
                "Present"
                if shifts_worked > 0
                else "Absent"
            )


            attendance_data.append({

                "guard_id": guard.id,

                "employee_id": (
                    guard.employee_id or "N/A"
                ),

                "guard_name": (
                    guard.name or "Unknown"
                ),

                "work_date": work_date,

                "shift_1": shift_1_status,

                "shift_1_site": shift_1_site,

                "shift_2": shift_2_status,

                "shift_2_site": shift_2_site,

                "shifts_worked": shifts_worked,

                "attendance_status": (
                    attendance_status
                )
            })


        return attendance_data


    except Exception as e:

        print(
            f"Unable to load guard attendance: {e}"
        )

        return []


    finally:

        db.close()


# ==================================================
# SITE DAILY ATTENDANCE
#
# SOURCE OF TRUTH:
# GuardWorkLog
# ==================================================

def get_site_daily_attendance(
    work_date,
    site_id=None
):

    db = SessionLocal()

    try:

        # ==========================================
        # GET ACTIVE SITES
        # ==========================================

        sites_query = (
            db.query(Site)
            .filter(
                func.lower(
                    func.coalesce(
                        Site.status,
                        ""
                    )
                ) == "active"
            )
        )


        if site_id is not None:

            sites_query = sites_query.filter(
                Site.id == site_id
            )


        sites = (
            sites_query
            .order_by(
                Site.site_code.asc()
            )
            .all()
        )


        # ==========================================
        # GET PRESENT SHIFT LOGS
        # ==========================================

        logs_query = (
            db.query(GuardWorkLog)
            .options(
                joinedload(
                    GuardWorkLog.guard
                ),
                joinedload(
                    GuardWorkLog.site
                )
            )
            .filter(
                GuardWorkLog.work_date == work_date,
                GuardWorkLog.status == "Present"
            )
        )


        if site_id is not None:

            logs_query = logs_query.filter(
                GuardWorkLog.site_id == site_id
            )


        logs = logs_query.all()


        # ==========================================
        # CREATE SITE ATTENDANCE MAP
        # ==========================================

        site_map = {}


        for log in logs:

            if log.site_id not in site_map:

                site_map[
                    log.site_id
                ] = {

                    "shift_1_guards": [],

                    "shift_2_guards": []
                }


            guard_name = (
                log.guard.name
                if log.guard
                else "Unknown Guard"
            )


            if log.shift_number == 1:

                site_map[
                    log.site_id
                ]["shift_1_guards"].append(
                    guard_name
                )


            elif log.shift_number == 2:

                site_map[
                    log.site_id
                ]["shift_2_guards"].append(
                    guard_name
                )


        # ==========================================
        # BUILD SITE ATTENDANCE DATA
        # ==========================================

        attendance_data = []


        for site in sites:

            site_attendance = site_map.get(
                site.id,
                {
                    "shift_1_guards": [],
                    "shift_2_guards": []
                }
            )


            shift_1_guards = (
                site_attendance["shift_1_guards"]
            )

            shift_2_guards = (
                site_attendance["shift_2_guards"]
            )


            shift_1_count = len(
                shift_1_guards
            )

            shift_2_count = len(
                shift_2_guards
            )


            total_shifts = (
                shift_1_count
                + shift_2_count
            )


            guards_present = len(
                set(
                    shift_1_guards
                    + shift_2_guards
                )
            )


            attendance_data.append({

                "site_id": site.id,

                "site_code": (
                    site.site_code or "N/A"
                ),

                "site_name": (
                    site.name or "Unknown"
                ),

                "guards_required": int(
                    site.guards_required or 0
                ),

                "guards_present": guards_present,

                "shift_1_count": shift_1_count,

                "shift_2_count": shift_2_count,

                "total_shifts": total_shifts,

                "shift_1_guards": (
                    ", ".join(shift_1_guards)
                    if shift_1_guards
                    else "-"
                ),

                "shift_2_guards": (
                    ", ".join(shift_2_guards)
                    if shift_2_guards
                    else "-"
                ),

                "attendance_status": (

                    "Covered"

                    if total_shifts > 0

                    else "No Coverage"
                )
            })


        return attendance_data


    except Exception as e:

        print(
            f"Unable to load site attendance: {e}"
        )

        return []


    finally:

        db.close()


# ==================================================
# GUARD ATTENDANCE SUMMARY
# ==================================================

def get_guard_attendance_summary(
    work_date,
    site_id=None
):

    attendance = get_guard_daily_attendance(
        work_date=work_date,
        site_id=site_id
    )


    total_guards = len(
        attendance
    )


    present_guards = sum(
        1
        for item in attendance
        if item["attendance_status"] == "Present"
    )


    absent_guards = sum(
        1
        for item in attendance
        if item["attendance_status"] == "Absent"
    )


    shift_1_count = sum(
        1
        for item in attendance
        if item["shift_1"] == "Present"
    )


    shift_2_count = sum(
        1
        for item in attendance
        if item["shift_2"] == "Present"
    )


    return {

        "total_guards": total_guards,

        "present_guards": present_guards,

        "absent_guards": absent_guards,

        "shift_1_count": shift_1_count,

        "shift_2_count": shift_2_count
    }


# ==================================================
# SITE ATTENDANCE SUMMARY
# ==================================================

def get_site_attendance_summary(
    work_date,
    site_id=None
):

    attendance = get_site_daily_attendance(
        work_date=work_date,
        site_id=site_id
    )


    total_sites = len(
        attendance
    )


    total_guards_required = sum(
        item["guards_required"]
        for item in attendance
    )


    shift_1_coverage = sum(
        item["shift_1_count"]
        for item in attendance
    )


    shift_2_coverage = sum(
        item["shift_2_count"]
        for item in attendance
    )


    return {

        "total_sites": total_sites,

        "total_guards_required": (
            total_guards_required
        ),

        "shift_1_coverage": (
            shift_1_coverage
        ),

        "shift_2_coverage": (
            shift_2_coverage
        )
    }