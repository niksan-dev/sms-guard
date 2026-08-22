from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from database.connection import SessionLocal
from database.models import (
    Site
)
from sqlalchemy.orm import joinedload
from database.payment import Payment
from database.company_settings import CompanySettings


# ==================================================
# MONTH START DATE
# ==================================================

def get_month_start(billing_date):

    return billing_date.replace(
        day=1
    )


# ==================================================
# MONTH END DATE
# ==================================================

def get_month_end(billing_date):

    month_start = get_month_start(
        billing_date
    )

    if month_start.month == 12:

        next_month = date(
            month_start.year + 1,
            1,
            1
        )

    else:

        next_month = date(
            month_start.year,
            month_start.month + 1,
            1
        )

    return next_month - timedelta(days=1)


# ==================================================
# GET COMPANY SETTINGS
# ==================================================

def get_invoice_prefix(bill_type):

    db = SessionLocal()

    try:

        settings = (
            db.query(CompanySettings)
            .first()
        )

        # GST INVOICE PREFIX
        if bill_type == "GST":

            if (
                settings
                and settings.gst_invoice_prefix
            ):

                return settings.gst_invoice_prefix

            return "GST"

        # NON-GST INVOICE PREFIX
        if (
            settings
            and settings.invoice_prefix
        ):

            return settings.invoice_prefix

        return "INV"

    finally:

        db.close()


# ==================================================
# GENERATE NEXT INVOICE NUMBER
# ==================================================

def generate_invoice_number(
    db,
    bill_type
):

    prefix = get_invoice_prefix(
        bill_type
    )

    current_year = date.today().year

    # Example:
    #
    # GST-2026-0001
    # INV-2026-0001

    last_payment = (
        db.query(Payment)
        .filter(
            Payment.invoice_number.like(
                f"{prefix}-{current_year}-%"
            )
        )
        .order_by(
            Payment.id.desc()
        )
        .first()
    )

    next_number = 1

    if last_payment:

        try:

            last_number = int(
                last_payment.invoice_number
                .split("-")[-1]
            )

            next_number = last_number + 1

        except (
            ValueError,
            IndexError
        ):

            next_number = 1

    return (
        f"{prefix}-"
        f"{current_year}-"
        f"{next_number:04d}"
    )


# ==================================================
# CALCULATE BILL AMOUNTS
# ==================================================

def calculate_bill_amounts(
    subtotal,
    bill_type,
    gst_percentage=18.0,
    interstate=False
):

    subtotal = float(
        subtotal or 0
    )

    gst_percentage = float(
        gst_percentage or 0
    )

    # ----------------------------------------------
    # NON GST
    # ----------------------------------------------

    if bill_type == "Non-GST":

        return {
            "subtotal": subtotal,
            "gst_percentage": 0.0,
            "cgst_amount": 0.0,
            "sgst_amount": 0.0,
            "igst_amount": 0.0,
            "total_amount": subtotal
        }


    # ----------------------------------------------
    # GST CALCULATION
    # ----------------------------------------------

    gst_amount = (
        subtotal
        * gst_percentage
        / 100
    )

    cgst_amount = 0.0
    sgst_amount = 0.0
    igst_amount = 0.0


    # Interstate → IGST
    if interstate:

        igst_amount = gst_amount


    # Same State → CGST + SGST
    else:

        cgst_amount = gst_amount / 2
        sgst_amount = gst_amount / 2


    total_amount = (
        subtotal
        + cgst_amount
        + sgst_amount
        + igst_amount
    )

    return {

        "subtotal": round(
            subtotal,
            2
        ),

        "gst_percentage": gst_percentage,

        "cgst_amount": round(
            cgst_amount,
            2
        ),

        "sgst_amount": round(
            sgst_amount,
            2
        ),

        "igst_amount": round(
            igst_amount,
            2
        ),

        "total_amount": round(
            total_amount,
            2
        )
    }


# ==================================================
# GET PAYMENT STATUS
# ==================================================

def calculate_payment_status(
    total_amount,
    paid_amount,
    due_date=None
):

    total_amount = float(
        total_amount or 0
    )

    paid_amount = float(
        paid_amount or 0
    )

    # Fully Paid
    if paid_amount >= total_amount:

        return "Paid"


    # Partial Payment
    if paid_amount > 0:

        return "Partial"


    # Overdue
    if (
        due_date
        and due_date < date.today()
    ):

        return "Overdue"


    # Default
    return "Pending"


# ==================================================
# CREATE MONTHLY PAYMENT / BILL
# ==================================================

def create_monthly_payment(

    site_id,

    billing_date,

    subtotal,

    bill_type="GST",

    gst_percentage=18.0,

    due_date=None,

    interstate=False,

    notes=None
):

    db = SessionLocal()

    try:

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

            raise ValueError(
                "Site not found."
            )


        # ==========================================
        # BILLING PERIOD
        # ==========================================

        billing_month = get_month_start(
            billing_date
        )

        billing_start_date = (
            get_month_start(
                billing_date
            )
        )

        billing_end_date = (
            get_month_end(
                billing_date
            )
        )


        # ==========================================
        # CHECK DUPLICATE BILL
        # ==========================================

        existing_payment = (
            db.query(Payment)
            .filter(
                Payment.site_id == site_id,
                Payment.billing_month == billing_month
            )
            .first()
        )

        if existing_payment:

            raise ValueError(
                "A bill already exists for this site "
                "for the selected month."
            )


        # ==========================================
        # CALCULATE GST
        # ==========================================

        amounts = calculate_bill_amounts(

            subtotal=subtotal,

            bill_type=bill_type,

            gst_percentage=gst_percentage,

            interstate=interstate
        )


        # ==========================================
        # GENERATE INVOICE NUMBER
        # ==========================================

        invoice_number = (
            generate_invoice_number(
                db,
                bill_type
            )
        )


        # ==========================================
        # INITIAL PAYMENT VALUES
        # ==========================================

        paid_amount = 0.0

        balance_amount = (
            amounts["total_amount"]
        )

        payment_status = (
            calculate_payment_status(

                total_amount=(
                    amounts["total_amount"]
                ),

                paid_amount=paid_amount,

                due_date=due_date
            )
        )


        # ==========================================
        # CREATE PAYMENT
        # ==========================================

        payment = Payment(

            invoice_number=invoice_number,

            site_id=site.id,

            client_id=site.client_id,

            billing_month=billing_month,

            billing_start_date=(
                billing_start_date
            ),

            billing_end_date=(
                billing_end_date
            ),

            due_date=due_date,

            bill_type=bill_type,

            subtotal=(
                amounts["subtotal"]
            ),

            gst_percentage=(
                amounts["gst_percentage"]
            ),

            cgst_amount=(
                amounts["cgst_amount"]
            ),

            sgst_amount=(
                amounts["sgst_amount"]
            ),

            igst_amount=(
                amounts["igst_amount"]
            ),

            total_amount=(
                amounts["total_amount"]
            ),

            paid_amount=paid_amount,

            balance_amount=balance_amount,

            payment_status=payment_status,

            notes=notes
        )

        db.add(payment)

        db.commit()

        db.refresh(payment)

        return payment


    except IntegrityError:

        db.rollback()

        raise ValueError(
            "Unable to create bill. "
            "A duplicate invoice or billing record "
            "may already exist."
        )


    except Exception:

        db.rollback()

        raise


    finally:

        db.close()


# ==================================================
# RECORD PAYMENT
# ==================================================

def record_payment(

    payment_id,

    amount,

    payment_date=None,

    payment_method=None,

    transaction_reference=None
):

    db = SessionLocal()

    try:

        payment = (
            db.query(Payment)
            .filter(
                Payment.id == payment_id
            )
            .first()
        )

        if not payment:

            raise ValueError(
                "Payment record not found."
            )


        amount = float(
            amount or 0
        )


        if amount <= 0:

            raise ValueError(
                "Payment amount must be greater than zero."
            )


        remaining_amount = (
            payment.total_amount
            - payment.paid_amount
        )


        if amount > remaining_amount:

            raise ValueError(
                "Payment amount cannot be greater "
                "than the remaining balance."
            )


        # ==========================================
        # UPDATE AMOUNT
        # ==========================================

        payment.paid_amount = round(
            payment.paid_amount + amount,
            2
        )

        payment.balance_amount = round(
            payment.total_amount
            - payment.paid_amount,
            2
        )


        # ==========================================
        # UPDATE STATUS
        # ==========================================

        payment.payment_status = (
            calculate_payment_status(

                total_amount=payment.total_amount,

                paid_amount=payment.paid_amount,

                due_date=payment.due_date
            )
        )


        # ==========================================
        # PAYMENT DETAILS
        # ==========================================

        payment.payment_date = (
            payment_date
            or date.today()
        )

        payment.payment_method = (
            payment_method
        )

        payment.transaction_reference = (
            transaction_reference
        )


        db.commit()

        db.refresh(payment)

        return payment


    except Exception:

        db.rollback()

        raise


    finally:

        db.close()


# ==================================================
# REFRESH OVERDUE PAYMENTS
# ==================================================

def update_overdue_payments():

    db = SessionLocal()

    try:

        payments = (
            db.query(Payment)
            .filter(
                Payment.payment_status.in_(
                    ["Pending", "Partial"]
                )
            )
            .all()
        )

        updated_count = 0


        for payment in payments:

            if (
                payment.due_date
                and payment.due_date < date.today()
                and payment.paid_amount
                < payment.total_amount
            ):

                payment.payment_status = (
                    "Overdue"
                )

                updated_count += 1


        db.commit()

        return updated_count


    except Exception:

        db.rollback()

        raise


    finally:

        db.close()


# ==================================================
# GET ALL PAYMENTS
# ==================================================

def get_all_payments():

    update_overdue_payments()

    db = SessionLocal()

    try:

        payments = (
            db.query(Payment)
            .options(
                joinedload(Payment.site)
            )
            .order_by(
                Payment.created_at.desc()
            )
            .all()
        )

        return payments

    finally:

        db.close()


# ==================================================
# GET PAYMENT BY ID
# ==================================================

def get_payment_by_id(payment_id):

    db = SessionLocal()

    try:

        payment = (
            db.query(Payment)
            .options(
                joinedload(Payment.site)
            )
            .filter(
                Payment.id == payment_id
            )
            .first()
        )

        return payment

    finally:

        db.close()

def get_payments_by_site(site_id):

    db = SessionLocal()

    try:

        payments = (
            db.query(Payment)
            .options(
                joinedload(Payment.site)
            )
            .filter(
                Payment.site_id == site_id
            )
            .order_by(
                Payment.billing_year.desc(),
                Payment.billing_month.desc()
            )
            .all()
        )

        return payments

    finally:

        db.close()

def update_overdue_payments():

    db = SessionLocal()

    try:

        today = date.today()

        payments = (
            db.query(Payment)
            .filter(
                Payment.payment_status.in_(
                    ["Pending", "Partially Paid"]
                )
            )
            .filter(
                Payment.due_date < today
            )
            .all()
        )

        for payment in payments:

            payment.payment_status = "Overdue"

        db.commit()

        return True

    except Exception as e:

        db.rollback()

        raise e

    finally:

        db.close()

def get_payment_statistics():

    update_overdue_payments()

    db = SessionLocal()

    try:

        total_payments = db.query(Payment).count()

        paid_payments = (
            db.query(Payment)
            .filter(
                Payment.payment_status == "Paid"
            )
            .count()
        )

        pending_payments = (
            db.query(Payment)
            .filter(
                Payment.payment_status == "Pending"
            )
            .count()
        )

        overdue_payments = (
            db.query(Payment)
            .filter(
                Payment.payment_status == "Overdue"
            )
            .count()
        )

        partially_paid = (
            db.query(Payment)
            .filter(
                Payment.payment_status == "Partially Paid"
            )
            .count()
        )

        return {
            "total": total_payments,
            "paid": paid_payments,
            "pending": pending_payments,
            "overdue": overdue_payments,
            "partially_paid": partially_paid
        }

    finally:

        db.close()


def record_payment(
    payment_id,
    amount,
    payment_date,
    payment_mode,
    transaction_reference=None,
    remarks=None
):

    db = SessionLocal()

    try:

        payment = (
            db.query(Payment)
            .filter(
                Payment.id == payment_id
            )
            .first()
        )

        if not payment:

            raise ValueError(
                "Payment record not found."
            )

        amount = float(amount)

        if amount <= 0:

            raise ValueError(
                "Payment amount must be greater than zero."
            )

        current_paid = float(
            payment.paid_amount or 0
        )

        total_amount = float(
            payment.total_amount or 0
        )

        new_paid_amount = (
            current_paid + amount
        )

        # Prevent overpayment
        if new_paid_amount > total_amount:

            raise ValueError(
                f"Payment amount exceeds balance. "
                f"Remaining balance: ₹ {total_amount - current_paid:,.2f}"
            )

        payment.paid_amount = new_paid_amount
        payment.payment_date = payment_date
        payment.payment_mode = payment_mode
        payment.transaction_reference = (
            transaction_reference.strip()
            if transaction_reference
            else None
        )
        payment.remarks = (
            remarks.strip()
            if remarks
            else None
        )

        # Calculate remaining balance
        remaining_amount = (
            total_amount - new_paid_amount
        )

        if remaining_amount <= 0:

            payment.payment_status = "Paid"

        else:

            if payment.due_date < date.today():

                payment.payment_status = "Overdue"

            else:

                payment.payment_status = (
                    "Partially Paid"
                )

        db.commit()

        db.refresh(payment)

        return payment

    except Exception as e:

        db.rollback()

        raise e

    finally:

        db.close()