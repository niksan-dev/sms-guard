from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from database.connection import SessionLocal
from database.guard_daily_work import GuardDailyWork


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

def get_guard_daily_attendance(work_date):

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
                GuardDailyWork.guard_id,
                GuardDailyWork.shift_number
            )
            .all()
        )

        attendance = []

        for record in records:

            attendance.append({

                "record_id": record.id,

                "guard_id": record.guard_id,

                "guard_name": (
                    record.guard.name
                    if record.guard
                    else "Unknown Guard"
                ),

                "site_id": record.site_id,

                "site_name": (
                    record.site.name
                    if record.site
                    else "Unknown Site"
                ),

                "shift_number": record.shift_number,

                "status": record.status,

                "work_date": record.work_date
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