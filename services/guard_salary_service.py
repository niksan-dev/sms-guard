from calendar import monthrange
from datetime import datetime

from sqlalchemy import extract
from sqlalchemy.orm import joinedload

from database.connection import SessionLocal
from database.guard_daily_work import GuardDailyWork
from database.guard_advance import GuardAdvance
from database.guard_salary_slip import GuardSalarySlip


# ==================================================
# HELPERS
# ==================================================

def get_days_in_month(year, month):

    return monthrange(
        int(year),
        int(month)
    )[1]


def generate_salary_slip_number(
    year,
    month,
    guard_id
):

    return (
        f"SAL-{int(year):04d}"
        f"{int(month):02d}-"
        f"{int(guard_id):04d}"
    )


# ==================================================
# GET GUARD MONTHLY SALARY DATA
# ==================================================

def get_guard_salary_data(
    guard_id,
    year,
    month
):

    db = SessionLocal()

    try:

        guard_id = int(guard_id)
        year = int(year)
        month = int(month)

        # ------------------------------------------
        # GET WORK RECORDS
        # ------------------------------------------

        work_records = (

            db.query(GuardDailyWork)

            .options(
                joinedload(
                    GuardDailyWork.guard
                ),
                joinedload(
                    GuardDailyWork.site
                )
            )

            .filter(
                GuardDailyWork.guard_id == guard_id,

                extract(
                    "year",
                    GuardDailyWork.work_date
                ) == year,

                extract(
                    "month",
                    GuardDailyWork.work_date
                ) == month
            )

            .order_by(
                GuardDailyWork.work_date.asc(),
                GuardDailyWork.shift_number.asc()
            )

            .all()
        )

        if not work_records:

            return None

        guard = work_records[0].guard

        # ------------------------------------------
        # DAYS IN MONTH
        # ------------------------------------------

        total_days = get_days_in_month(
            year,
            month
        )

        # ------------------------------------------
        # PRESENT RECORDS
        # ------------------------------------------

        present_records = [
            record
            for record in work_records
            if (record.status or "").lower()
            == "present"
        ]

        # ------------------------------------------
        # SHIFT COUNTS
        # ------------------------------------------

        shift_1_count = sum(
            1
            for record in present_records
            if record.shift_number == 1
        )

        shift_2_count = sum(
            1
            for record in present_records
            if record.shift_number == 2
        )

        total_shifts = (
            shift_1_count
            + shift_2_count
        )

        # ------------------------------------------
        # PRESENT DAYS
        #
        # A day counts once even if guard
        # worked two shifts.
        # ------------------------------------------

        present_days = len({
            record.work_date
            for record in present_records
        })

        # ------------------------------------------
        # MONTHLY SALARY
        # ------------------------------------------

        monthly_salary = float(
            guard.monthly_salary or 0
        )

        # ------------------------------------------
        # SHIFT RATE
        #
        # Monthly salary / calendar days
        # ------------------------------------------

        shift_rate = (
            monthly_salary / total_days
            if total_days > 0
            else 0.0
        )

        # ------------------------------------------
        # GROSS SALARY
        #
        # Shift rate × total shifts
        # ------------------------------------------

        gross_salary = (
            shift_rate * total_shifts
        )

        # ------------------------------------------
        # GET ADVANCES
        # ------------------------------------------

        advances = (

            db.query(GuardAdvance)

            .filter(

                GuardAdvance.guard_id
                == guard_id,

                extract(
                    "year",
                    GuardAdvance.record_date
                ) == year,

                extract(
                    "month",
                    GuardAdvance.record_date
                ) == month
            )

            .order_by(
                GuardAdvance.record_date.asc(),
                GuardAdvance.id.asc()
            )

            .all()
        )

        # ------------------------------------------
        # TOTAL ADVANCE
        # ------------------------------------------

        total_advance = sum(
            float(
                advance.amount or 0
            )
            for advance in advances
        )

        # ------------------------------------------
        # NET PAYABLE
        # ------------------------------------------

        net_payable = (
            gross_salary
            - total_advance
        )

        return {

            "guard_id": guard.id,

            "employee_id": guard.employee_id,

            "guard_name": guard.name,

            "salary_month": month,

            "salary_year": year,

            "total_days": total_days,

            "present_days": present_days,

            "shift_1_count": shift_1_count,

            "shift_2_count": shift_2_count,

            "total_shifts": total_shifts,

            "monthly_salary": monthly_salary,

            "shift_rate": shift_rate,

            "gross_salary": gross_salary,

            "total_advance": total_advance,

            "net_payable": net_payable,

            "work_records": work_records,

            "advances": advances
        }

    finally:

        db.close()


# ==================================================
# SAVE GUARD SALARY SLIP
# ==================================================

def create_guard_salary_slip(
    guard_id,
    year,
    month
):

    db = SessionLocal()

    try:

        data = get_guard_salary_data(
            guard_id,
            year,
            month
        )

        if not data:

            return (
                False,
                "No work records found for this guard.",
                None
            )

        # ------------------------------------------
        # SLIP NUMBER
        # ------------------------------------------

        slip_number = generate_salary_slip_number(
            year,
            month,
            guard_id
        )

        # ------------------------------------------
        # CHECK EXISTING SLIP
        # ------------------------------------------

        existing = (

            db.query(GuardSalarySlip)

            .filter(
                GuardSalarySlip.slip_number
                == slip_number
            )

            .first()
        )

        if existing:

            # Update existing slip
            existing.slip_date = datetime.utcnow()

            existing.total_days = data[
                "total_days"
            ]

            existing.present_days = data[
                "present_days"
            ]

            existing.shift_1_count = data[
                "shift_1_count"
            ]

            existing.shift_2_count = data[
                "shift_2_count"
            ]

            existing.total_shifts = data[
                "total_shifts"
            ]

            existing.monthly_salary = data[
                "monthly_salary"
            ]

            existing.shift_rate = data[
                "shift_rate"
            ]

            existing.gross_salary = data[
                "gross_salary"
            ]

            existing.total_advance = data[
                "total_advance"
            ]

            existing.net_payable = data[
                "net_payable"
            ]

            existing.updated_at = datetime.utcnow()

            db.commit()

            db.refresh(existing)

            return (
                True,
                "Salary slip updated successfully.",
                existing
            )

        # ------------------------------------------
        # CREATE NEW SLIP
        # ------------------------------------------

        slip = GuardSalarySlip(

            slip_number=slip_number,

            guard_id=data[
                "guard_id"
            ],

            salary_month=data[
                "salary_month"
            ],

            salary_year=data[
                "salary_year"
            ],

            slip_date=datetime.utcnow(),

            total_days=data[
                "total_days"
            ],

            present_days=data[
                "present_days"
            ],

            shift_1_count=data[
                "shift_1_count"
            ],

            shift_2_count=data[
                "shift_2_count"
            ],

            total_shifts=data[
                "total_shifts"
            ],

            monthly_salary=data[
                "monthly_salary"
            ],

            shift_rate=data[
                "shift_rate"
            ],

            gross_salary=data[
                "gross_salary"
            ],

            total_advance=data[
                "total_advance"
            ],

            net_payable=data[
                "net_payable"
            ],

            status="Generated"
        )

        db.add(slip)

        db.commit()

        db.refresh(slip)

        return (
            True,
            "Salary slip generated successfully.",
            slip
        )

    except Exception as e:

        db.rollback()

        return (
            False,
            f"Unable to generate salary slip: {str(e)}",
            None
        )

    finally:

        db.close()


# ==================================================
# GET SAVED SALARY SLIP
# ==================================================

def get_guard_salary_slip(
    guard_id,
    year,
    month
):

    db = SessionLocal()

    try:

        slip_number = generate_salary_slip_number(
            year,
            month,
            guard_id
        )

        return (

            db.query(GuardSalarySlip)

            .options(
                joinedload(
                    GuardSalarySlip.guard
                )
            )

            .filter(
                GuardSalarySlip.slip_number
                == slip_number
            )

            .first()
        )

    finally:

        db.close()


# ==================================================
# GET ALL SALARY SLIPS FOR MONTH
# ==================================================

def get_monthly_salary_slips(
    year,
    month
):

    db = SessionLocal()

    try:

        return (

            db.query(GuardSalarySlip)

            .options(
                joinedload(
                    GuardSalarySlip.guard
                )
            )

            .filter(
                GuardSalarySlip.salary_year
                == int(year),

                GuardSalarySlip.salary_month
                == int(month)
            )

            .order_by(
                GuardSalarySlip.slip_number.asc()
            )

            .all()
        )

    finally:

        db.close()