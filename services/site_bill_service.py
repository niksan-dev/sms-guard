from calendar import monthrange
from datetime import datetime

from sqlalchemy import extract
from sqlalchemy.orm import joinedload

from database.connection import SessionLocal
from database.guard_daily_work import GuardDailyWork
from database.site_bill import SiteBill

from database.models import CompanySettings


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
        # GET WORK RECORDS FOR SITE / MONTH
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
                GuardDailyWork.site_id == site_id,

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
        # PRESENT RECORDS ONLY
        # ------------------------------------------

        present_records = [
            record
            for record in work_records
            if (record.status or "").lower() == "present"
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
        # ACTUAL PRESENT DAYS
        #
        # A date is considered PRESENT when
        # there is at least one Present shift.
        #
        # Example:
        #
        # 01 -> Shift 1 = Present
        # 02 -> no record
        # 03 -> Shift 1 + Shift 2
        #
        # Present Days = 2
        # ------------------------------------------

        present_dates = {
            record.work_date
            for record in present_records
            if record.work_date is not None
        }

        present_days = len(present_dates)

        # ------------------------------------------
        # CALENDAR DAYS
        #
        # Keep this separately because the rate
        # calculation is still based on the full
        # month's calendar days.
        # ------------------------------------------

        calendar_days = get_days_in_month(
            year,
            month
        )

        # ------------------------------------------
        # SITE RATE
        # ------------------------------------------

        monthly_rate = float(
            site.guard_rate or 0
        )

        # ------------------------------------------
        # RATE PER SHIFT
        #
        # Monthly guard rate represents the rate
        # for one guard for the full month.
        #
        # 2 shifts per day.
        # ------------------------------------------

        shift_rate = (
            monthly_rate / calendar_days #this was devided by 2
            if calendar_days > 0
            else 0.0
        )

        # ------------------------------------------
        # GROSS REVENUE
        # ------------------------------------------

        gross_amount = (
            shift_rate * total_shifts
        )

        # ------------------------------------------
        # RETURN BILL DATA
        # ------------------------------------------

        return {

            "site_id": site.id,

            "site_code": site.site_code,

            "site_name": site.name,

            "billing_month": month,

            "billing_year": year,

            # IMPORTANT:
            # This is now ACTUAL PRESENT DAYS,
            # not 28/30/31.
            "total_days": present_days,

            # Useful if we need it later.
            "calendar_days": calendar_days,

            "present_days": present_days,

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
    month
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
        # COMPANY GST SETTINGS
        # ------------------------------------------

        company_settings = (
            db.query(CompanySettings)
            .first()
        )

        if not company_settings:
            return (
                False,
                "Company settings not found.",
                None
            )

        

        cgst_rate = float(
            company_settings.cgst_rate or 0.0
        )

        sgst_rate = float(
            company_settings.sgst_rate or 0.0
        )

        # ------------------------------------------
        # GST CALCULATION
        # ------------------------------------------

        gross_amount = float(
            data["gross_amount"] or 0.0
        )

        cgst_amount = (
            gross_amount
            * cgst_rate
            / 100
        )

        sgst_amount = (
            gross_amount
            * sgst_rate
            / 100
        )

        total_amount = (
            gross_amount
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