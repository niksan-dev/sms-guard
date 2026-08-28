from calendar import monthrange
from datetime import datetime

from sqlalchemy import extract
from sqlalchemy.orm import joinedload

from database.connection import SessionLocal
from database.guard_daily_work import GuardDailyWork
from database.site_bill import SiteBill


# ==================================================
# HELPERS
# ==================================================

def get_days_in_month(year, month):

    return monthrange(
        int(year),
        int(month)
    )[1]


def generate_bill_number(
    year,
    month,
    site_id
):

    return (
        f"INV-{int(year):04d}"
        f"{int(month):02d}-"
        f"{int(site_id):04d}"
    )


# ==================================================
# GET SITE MONTHLY BILL DATA
# ==================================================

def get_site_bill_data(
    site_id,
    year,
    month
):

    db = SessionLocal()

    try:

        site_id = int(site_id)
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

                GuardDailyWork.site_id
                == site_id,

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

        site = work_records[0].site

        # ------------------------------------------
        # DAYS IN MONTH
        # ------------------------------------------

        total_days = get_days_in_month(
            year,
            month
        )

        # ------------------------------------------
        # PRESENT RECORDS ONLY
        # ------------------------------------------

        present_records = [
            record
            for record in work_records
            if (record.status or "").lower()
            == "present"
        ]

        # ------------------------------------------
        # SHIFT COUNTS
        #
        # These count guard-shifts.
        #
        # If two guards work Shift 1,
        # shift_1_count = 2.
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
        # SITE RATE
        # ------------------------------------------

        monthly_rate = float(
            site.guard_rate or 0
        )

        # ------------------------------------------
        # RATE PER SHIFT
        # ------------------------------------------

        shift_rate = (
            monthly_rate / total_days
            if total_days > 0
            else 0.0
        )

        # ------------------------------------------
        # GROSS REVENUE
        # ------------------------------------------

        gross_amount = (
            shift_rate * total_shifts
        )

        return {

            "site_id": site.id,

            "site_code": site.site_code,

            "site_name": site.name,

            "billing_month": month,

            "billing_year": year,

            "total_days": total_days,

            "shift_1_count": shift_1_count,

            "shift_2_count": shift_2_count,

            "total_shifts": total_shifts,

            "monthly_rate": monthly_rate,

            "shift_rate": shift_rate,

            "gross_amount": gross_amount,

            "work_records": work_records
        }

    finally:

        db.close()


# ==================================================
# CREATE / UPDATE SITE BILL
# ==================================================

def create_site_bill(
    site_id,
    year,
    month,
    cgst_rate=0.0,
    sgst_rate=0.0
):

    db = SessionLocal()

    try:

        data = get_site_bill_data(
            site_id,
            year,
            month
        )

        if not data:

            return (
                False,
                "No site work records found for this month.",
                None
            )

        # ------------------------------------------
        # GST
        # ------------------------------------------

        cgst_rate = float(
            cgst_rate or 0
        )

        sgst_rate = float(
            sgst_rate or 0
        )

        cgst_amount = (
            data["gross_amount"]
            * cgst_rate
            / 100
        )

        sgst_amount = (
            data["gross_amount"]
            * sgst_rate
            / 100
        )

        total_amount = (
            data["gross_amount"]
            + cgst_amount
            + sgst_amount
        )

        # ------------------------------------------
        # BILL NUMBER
        # ------------------------------------------

        bill_number = generate_bill_number(
            year,
            month,
            site_id
        )

        # ------------------------------------------
        # CHECK EXISTING
        # ------------------------------------------

        existing = (

            db.query(SiteBill)

            .filter(
                SiteBill.bill_number
                == bill_number
            )

            .first()
        )

        if existing:

            existing.bill_date = datetime.utcnow()

            existing.total_days = data[
                "total_days"
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

            existing.monthly_rate = data[
                "monthly_rate"
            ]

            existing.shift_rate = data[
                "shift_rate"
            ]

            existing.gross_amount = data[
                "gross_amount"
            ]

            existing.cgst_amount = (
                cgst_amount
            )

            existing.sgst_amount = (
                sgst_amount
            )

            existing.total_amount = (
                total_amount
            )

            existing.updated_at = datetime.utcnow()

            db.commit()

            db.refresh(existing)

            return (
                True,
                "Site bill updated successfully.",
                existing
            )

        # ------------------------------------------
        # CREATE NEW BILL
        # ------------------------------------------

        bill = SiteBill(

            bill_number=bill_number,

            site_id=data[
                "site_id"
            ],

            billing_month=data[
                "billing_month"
            ],

            billing_year=data[
                "billing_year"
            ],

            bill_date=datetime.utcnow(),

            total_days=data[
                "total_days"
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

            monthly_rate=data[
                "monthly_rate"
            ],

            shift_rate=data[
                "shift_rate"
            ],

            gross_amount=data[
                "gross_amount"
            ],

            cgst_amount=cgst_amount,

            sgst_amount=sgst_amount,

            total_amount=total_amount,

            status="Generated"
        )

        db.add(bill)

        db.commit()

        db.refresh(bill)

        return (
            True,
            "Site bill generated successfully.",
            bill
        )

    except Exception as e:

        db.rollback()

        return (
            False,
            f"Unable to generate site bill: {str(e)}",
            None
        )

    finally:

        db.close()


# ==================================================
# GET SAVED SITE BILL
# ==================================================

def get_site_bill(
    site_id,
    year,
    month
):

    db = SessionLocal()

    try:

        bill_number = generate_bill_number(
            year,
            month,
            site_id
        )

        return (

            db.query(SiteBill)

            .options(
                joinedload(
                    SiteBill.site
                )
            )

            .filter(
                SiteBill.bill_number
                == bill_number
            )

            .first()
        )

    finally:

        db.close()


# ==================================================
# GET ALL SITE BILLS FOR MONTH
# ==================================================

def get_monthly_site_bills(
    year,
    month
):

    db = SessionLocal()

    try:

        return (

            db.query(SiteBill)

            .options(
                joinedload(
                    SiteBill.site
                )
            )

            .filter(

                SiteBill.billing_year
                == int(year),

                SiteBill.billing_month
                == int(month)
            )

            .order_by(
                SiteBill.bill_number.asc()
            )

            .all()
        )

    finally:

        db.close()