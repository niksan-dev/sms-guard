from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from database.connection import SessionLocal
from database.guard_daily_work import GuardDailyWork



from sqlalchemy import func
from datetime import date
import calendar



from database.models import Guard
from database.models import Site




# ==================================================
# CREATE DAILY WORK RECORD
# ==================================================

def create_guard_daily_work(
    guard_id,
    site_id,
    work_date,
    shift_number,
    status="Present"
):

    db = SessionLocal()

    try:

        guard_id = int(guard_id)
        site_id = int(site_id)
        shift_number = int(shift_number)

        # ------------------------------------------
        # VALIDATE SHIFT
        # ------------------------------------------

        if shift_number not in (1, 2):

            return (
                False,
                "Shift number must be 1 or 2."
            )

        # ------------------------------------------
        # CHECK IF GUARD ALREADY HAS THIS SHIFT
        #
        # One guard cannot work Shift 1 at two sites
        # on the same date.
        #
        # One guard cannot work Shift 2 at two sites
        # on the same date.
        # ------------------------------------------

        existing_record = (
            db.query(GuardDailyWork)
            .filter(
                GuardDailyWork.guard_id == guard_id,
                GuardDailyWork.work_date == work_date,
                GuardDailyWork.shift_number == shift_number
            )
            .first()
        )

        if existing_record:

            return (
                False,
                f"This guard is already assigned to "
                f"Shift {shift_number} on this date."
            )

        # ------------------------------------------
        # CREATE RECORD
        # ------------------------------------------

        daily_work = GuardDailyWork(

            guard_id=guard_id,

            site_id=site_id,

            work_date=work_date,

            shift_number=shift_number,

            status=status or "Present"
        )

        db.add(daily_work)

        db.commit()

        return (
            True,
            "Shift recorded successfully."
        )

    except IntegrityError:

        db.rollback()

        return (
            False,
            "Unable to save this shift. "
            "The guard may already be assigned to this shift."
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
# GET DAILY WORK RECORDS BY DATE
# ==================================================

def get_daily_work_records(work_date):

    db = SessionLocal()

    try:

        records = (
            db.query(GuardDailyWork)
            .options(
                joinedload(GuardDailyWork.guard),
                joinedload(GuardDailyWork.site)
            )
            .filter(
                GuardDailyWork.work_date == work_date
            )
            .order_by(
                GuardDailyWork.shift_number.asc(),
                GuardDailyWork.id.desc()
            )
            .all()
        )

        return records

    except Exception:

        return []

    finally:

        db.close()


# ==================================================
# DELETE DAILY WORK RECORD
# ==================================================

def delete_daily_work(record_id):

    db = SessionLocal()

    try:

        record = (
            db.query(GuardDailyWork)
            .filter(
                GuardDailyWork.id == record_id
            )
            .first()
        )

        if not record:

            return (
                False,
                "Work record not found."
            )

        db.delete(record)

        db.commit()

        return (
            True,
            "Work record deleted successfully."
        )

    except Exception as e:

        db.rollback()

        return (
            False,
            f"Unable to delete work record: {str(e)}"
        )

    finally:

        db.close()


# ==================================================
# GET DAILY WORK SUMMARY
# ==================================================

def get_daily_work_summary(work_date):

    db = SessionLocal()

    try:

        records = (
            db.query(GuardDailyWork)
            .filter(
                GuardDailyWork.work_date == work_date
            )
            .all()
        )

        total_shifts = len(records)

        shift_1_count = sum(
            1
            for record in records
            if record.shift_number == 1
        )

        shift_2_count = sum(
            1
            for record in records
            if record.shift_number == 2
        )

        unique_guards = len(
            {
                record.guard_id
                for record in records
            }
        )

        unique_sites = len(
            {
                record.site_id
                for record in records
            }
        )

        return {

            "total_shifts": total_shifts,

            "shift_1_count": shift_1_count,

            "shift_2_count": shift_2_count,

            "unique_guards": unique_guards,

            "unique_sites": unique_sites
        }

    finally:

        db.close()


# ==================================================
# GET GUARD DAILY ATTENDANCE
# ==================================================

def get_guard_daily_attendance(selected_date):

    db = SessionLocal()

    try:

        # Actual days in the month of selected date
        total_days_in_month = calendar.monthrange(
            selected_date.year,
            selected_date.month
        )[1]

        records = (
            db.query(GuardDailyWork)
            .options(
                joinedload(GuardDailyWork.guard),
                joinedload(GuardDailyWork.site)
            )
            .filter(
                GuardDailyWork.work_date == selected_date
            )
            .order_by(
                GuardDailyWork.guard_id,
                GuardDailyWork.shift_number
            )
            .all()
        )

        attendance = []

        for record in records:

            guard = record.guard
            site = record.site

            monthly_salary = float(
                guard.monthly_salary or 0
            ) if guard else 0.0

            # Salary calculations based on actual days
            daily_salary = (
                monthly_salary / total_days_in_month
                if total_days_in_month > 0
                else 0
            )

            salary_per_shift = daily_salary

            # Only Present generates salary
            actual_salary = (
                salary_per_shift
                if record.status == "Present"
                else 0.0
            )

            attendance.append({

                "id": record.id,

                "work_date": record.work_date,

                "guard_id": record.guard_id,

                "employee_id": (
                    guard.employee_id
                    if guard and guard.employee_id
                    else "-"
                ),

                "guard_name": (
                    guard.name
                    if guard and guard.name
                    else "Unknown Guard"
                ),

                "site_id": record.site_id,

                "site_code": (
                    site.site_code
                    if site and site.site_code
                    else "-"
                ),

                "site_name": (
                    site.name
                    if site and site.name
                    else "Unknown Site"
                ),

                "shift_number": record.shift_number,

                "status": record.status or "Present",

                # Financial information
                "total_days": total_days_in_month,

                "monthly_salary": monthly_salary,

                "daily_salary": round(
                    daily_salary,
                    2
                ),

                "salary_per_shift": round(
                    salary_per_shift,
                    2
                ),

                "actual_salary": round(
                    actual_salary,
                    2
                ),
            })

        return attendance

    finally:

        db.close()


# ==================================================
# GET SITE DAILY ATTENDANCE
# ==================================================

def get_site_daily_attendance(work_date):

    db = SessionLocal()

    try:

        records = (
            db.query(GuardDailyWork)
            .options(
                joinedload(GuardDailyWork.guard),
                joinedload(GuardDailyWork.site)
            )
            .filter(
                GuardDailyWork.work_date == work_date
            )
            .order_by(
                GuardDailyWork.site_id,
                GuardDailyWork.shift_number
            )
            .all()
        )

        attendance = []

        for record in records:

            attendance.append({

                "record_id": record.id,

                "site_id": record.site_id,

                "site_name": (
                    record.site.name
                    if record.site
                    else "Unknown Site"
                ),

                "guard_id": record.guard_id,

                "guard_name": (
                    record.guard.name
                    if record.guard
                    else "Unknown Guard"
                ),

                "shift_number": record.shift_number,

                "status": record.status,

                "work_date": record.work_date
            })

        return attendance

    finally:

        db.close()

def get_guard_monthly_attendance(year, month):

    db = SessionLocal()

    try:

        total_days_in_month = calendar.monthrange(
            year,
            month
        )[1]

        start_date = date(
            year,
            month,
            1
        )

        end_date = date(
            year,
            month,
            total_days_in_month
        )

        guards = (
            db.query(Guard)
            .order_by(
                Guard.employee_id
            )
            .all()
        )

        monthly_attendance = []

        for guard in guards:

            monthly_salary = float(
                guard.monthly_salary or 0
            )

            records = (
                db.query(GuardDailyWork)
                .filter(
                    GuardDailyWork.guard_id == guard.id,
                    GuardDailyWork.work_date >= start_date,
                    GuardDailyWork.work_date <= end_date,
                    GuardDailyWork.status == "Present"
                )
                .all()
            )

            present_dates = {
                record.work_date
                for record in records
            }

            present_days = len(present_dates)

            shift_1_count = sum(
                1
                for record in records
                if record.shift_number == 1
            )

            shift_2_count = sum(
                1
                for record in records
                if record.shift_number == 2
            )

            total_shifts = len(records)

            daily_salary = (
                monthly_salary / total_days_in_month
                if total_days_in_month > 0
                else 0
            )

            salary_per_shift = daily_salary / 2

            actual_salary = (
                total_shifts * salary_per_shift
            )

            monthly_attendance.append({

                "guard_id": guard.id,

                "employee_id": (
                    guard.employee_id or "-"
                ),

                "guard_name": (
                    guard.name or "Unknown Guard"
                ),

                "total_days": total_days_in_month,

                "monthly_salary": round(
                    monthly_salary,
                    2
                ),

                "present_days": present_days,

                "shift_1_count": shift_1_count,

                "shift_2_count": shift_2_count,

                "total_shifts": total_shifts,

                "actual_salary": round(
                    actual_salary,
                    2
                ),
            })

        return monthly_attendance

    finally:

        db.close()


def get_site_daily_attendance(selected_date):

    db = SessionLocal()

    try:

        total_days_in_month = calendar.monthrange(
            selected_date.year,
            selected_date.month
        )[1]

        records = (
            db.query(GuardDailyWork)
            .options(
                joinedload(GuardDailyWork.guard),
                joinedload(GuardDailyWork.site)
            )
            .filter(
                GuardDailyWork.work_date == selected_date
            )
            .order_by(
                GuardDailyWork.site_id,
                GuardDailyWork.shift_number,
                GuardDailyWork.guard_id
            )
            .all()
        )

        attendance = []

        for record in records:

            guard = record.guard
            site = record.site

            guard_rate = float(
                site.guard_rate or 0
            ) if site else 0.0

            daily_revenue = (
                guard_rate / total_days_in_month
                if total_days_in_month > 0
                else 0
            )

            revenue_per_shift = daily_revenue

            actual_revenue = (
                revenue_per_shift
                if record.status == "Present"
                else 0.0
            )

            attendance.append({

                "id": record.id,

                "work_date": record.work_date,

                "site_id": record.site_id,

                "site_code": (
                    site.site_code
                    if site and site.site_code
                    else "-"
                ),

                "site_name": (
                    site.name
                    if site and site.name
                    else "Unknown Site"
                ),

                "guards_required": (
                    site.guards_required
                    if site and site.guards_required
                    else 0
                ),

                "guard_rate": round(
                    guard_rate,
                    2
                ),

                "guard_id": record.guard_id,

                "employee_id": (
                    guard.employee_id
                    if guard and guard.employee_id
                    else "-"
                ),

                "guard_name": (
                    guard.name
                    if guard and guard.name
                    else "Unknown Guard"
                ),

                "shift_number": record.shift_number,

                "status": record.status or "Present",

                # Financial information
                "total_days": total_days_in_month,

                "daily_revenue": round(
                    daily_revenue,
                    2
                ),

                "revenue_per_shift": round(
                    revenue_per_shift,
                    2
                ),

                "actual_revenue": round(
                    actual_revenue,
                    2
                ),
            })

        return attendance

    finally:

        db.close()

def get_site_monthly_attendance(year, month):

    db = SessionLocal()

    try:

        total_days_in_month = calendar.monthrange(
            year,
            month
        )[1]

        start_date = date(
            year,
            month,
            1
        )

        end_date = date(
            year,
            month,
            total_days_in_month
        )

        sites = (
            db.query(Site)
            .order_by(
                Site.site_code
            )
            .all()
        )

        monthly_attendance = []

        for site in sites:

            guard_rate = float(
                site.guard_rate or 0
            )

            guards_required = int(
                site.guards_required or 0
            )

            records = (
                db.query(GuardDailyWork)
                .filter(
                    GuardDailyWork.site_id == site.id,
                    GuardDailyWork.work_date >= start_date,
                    GuardDailyWork.work_date <= end_date,
                    GuardDailyWork.status == "Present"
                )
                .all()
            )

            shift_1_count = sum(
                1
                for record in records
                if record.shift_number == 1
            )

            shift_2_count = sum(
                1
                for record in records
                if record.shift_number == 2
            )

            total_shifts = len(records)

            unique_guards = len({
                record.guard_id
                for record in records
            })

            # Financial calculation
            daily_revenue = (
                guard_rate / total_days_in_month
                if total_days_in_month > 0
                else 0
            )

            revenue_per_shift = daily_revenue / 2

            actual_revenue = (
                total_shifts * revenue_per_shift
            )

            # Expected shifts for attendance coverage
            required_shifts = (
                guards_required
                * total_days_in_month
                * 2
            )

            coverage_percent = (
                round(
                    (total_shifts / required_shifts) * 100,
                    2
                )
                if required_shifts > 0
                else 0
            )

            monthly_attendance.append({

                "site_id": site.id,

                "site_code": (
                    site.site_code or "-"
                ),

                "site_name": (
                    site.name or "Unknown Site"
                ),

                "total_days": total_days_in_month,

                "guard_rate": round(
                    guard_rate,
                    2
                ),

                "guards_required": guards_required,

                "shift_1_count": shift_1_count,

                "shift_2_count": shift_2_count,

                "total_shifts": total_shifts,

                "unique_guards": unique_guards,

                "required_shifts": required_shifts,

                "coverage_percent": coverage_percent,

                "actual_revenue": round(
                    actual_revenue,
                    2
                ),
            })

        return monthly_attendance

    finally:

        db.close()