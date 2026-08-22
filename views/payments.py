import streamlit as st

from datetime import date, timedelta

from database.connection import SessionLocal
from database.models import Site

from services.payment_service import (
    create_monthly_payment,
    record_payment,
    get_all_payments,
    get_payment_by_id,
    update_overdue_payments,
    get_payment_statistics,
)


# ==================================================
# PAGE
# ==================================================

def show_payments():

    st.title("💳 Payment Management")

    st.caption(
        "Generate bills, track payments, and manage overdue invoices."
    )

    tabs = st.tabs([
        "➕ Generate Bill",
        "💰 Record Payment",
        "📋 Payment Records"
    ])

    with tabs[0]:

        show_create_bill()

    with tabs[1]:

        show_record_payment()

    with tabs[2]:

        show_payment_records()


# ==================================================
# GET SITES
# ==================================================

def get_active_sites():

    db = SessionLocal()

    try:

        return (
            db.query(Site)
            .filter(
                Site.status == "Active"
            )
            .order_by(
                Site.name.asc()
            )
            .all()
        )

    finally:

        db.close()


# ==================================================
# CREATE BILL
# ==================================================

def show_create_bill():

    st.subheader("Create Monthly Bill")

    sites = get_active_sites()

    if not sites:

        st.warning(
            "No active sites found. Please create a site first."
        )

        return


    # Create display mapping
    site_options = {
        f"{site.site_code} - {site.name}": site.id
        for site in sites
    }


    with st.form(
        "create_bill_form",
        clear_on_submit=True
    ):

        # ==============================================
        # SITE
        # ==============================================

        selected_site = st.selectbox(
            "🏢 Select Site *",
            list(site_options.keys())
        )

        site_id = site_options[
            selected_site
        ]


        # ==============================================
        # BILL TYPE
        # ==============================================

        col1, col2 = st.columns(2)

        with col1:

            bill_type = st.selectbox(
                "📄 Bill Type *",
                [
                    "GST",
                    "Non-GST"
                ]
            )


        with col2:

            billing_date = st.date_input(
                "📅 Billing Month *",
                value=date.today()
            )


        # ==============================================
        # AMOUNT
        # ==============================================

        col1, col2 = st.columns(2)

        with col1:

            subtotal = st.number_input(
                "💰 Service Amount (₹) *",
                min_value=0.0,
                value=0.0,
                step=100.0
            )


        with col2:

            gst_percentage = st.number_input(
                "GST Percentage",
                min_value=0.0,
                max_value=100.0,
                value=18.0,
                step=0.5,
                disabled=(
                    bill_type == "Non-GST"
                )
            )


        # ==============================================
        # DUE DATE
        # ==============================================

        due_date = st.date_input(
            "⏰ Payment Due Date",
            value=(
                date.today()
                + timedelta(days=15)
            )
        )


        # ==============================================
        # GST TYPE
        # ==============================================

        interstate = False

        if bill_type == "GST":

            interstate = st.checkbox(
                "Interstate Supply (IGST)"
            )


        # ==============================================
        # NOTES
        # ==============================================

        notes = st.text_area(
            "📝 Notes / Description",
            placeholder=(
                "Example: Security guard service charges "
                "for this month"
            )
        )


        # ==============================================
        # PREVIEW
        # ==============================================

        st.divider()

        st.caption("Bill Preview")

        if bill_type == "GST":

            gst_amount = (
                subtotal
                * gst_percentage
                / 100
            )

            total_preview = (
                subtotal
                + gst_amount
            )

        else:

            gst_amount = 0
            total_preview = subtotal


        p1, p2, p3 = st.columns(3)

        p1.metric(
            "Subtotal",
            f"₹ {subtotal:,.2f}"
        )

        p2.metric(
            "GST",
            f"₹ {gst_amount:,.2f}"
        )

        p3.metric(
            "Total Amount",
            f"₹ {total_preview:,.2f}"
        )


        # ==============================================
        # SUBMIT
        # ==============================================

        submitted = st.form_submit_button(
            "➕ Generate Bill",
            use_container_width=True,
            type="primary"
        )


        if submitted:

            if subtotal <= 0:

                st.error(
                    "Service amount must be greater than ₹0."
                )

                return


            try:

                payment = create_monthly_payment(

                    site_id=site_id,

                    billing_date=billing_date,

                    subtotal=subtotal,

                    bill_type=bill_type,

                    gst_percentage=(
                        0
                        if bill_type == "Non-GST"
                        else gst_percentage
                    ),

                    due_date=due_date,

                    interstate=interstate,

                    notes=notes
                )


                st.success(
                    f"Bill created successfully! "
                    f"Invoice: {payment.invoice_number}"
                )


                st.info(
                    f"Billing Period: "
                    f"{payment.billing_start_date.strftime('%d-%b-%Y')} "
                    f"to "
                    f"{payment.billing_end_date.strftime('%d-%b-%Y')}"
                )


            except Exception as e:

                st.error(
                    f"Error creating bill: {str(e)}"
                )


# ==================================================
# PAYMENT RECORDS
# ==================================================

def show_payment_records():

    st.subheader("📋 Payment Records")

    statistics = get_payment_statistics()

    col1, col2, col3, col4, col5 = st.columns(5)


    with col1:

        st.metric(
            "Total Bills",
            statistics["total"]
        )


    with col2:

        st.metric(
            "Paid",
            statistics["paid"]
        )


    with col3:

        st.metric(
            "Pending",
            statistics["pending"]
        )


    with col4:

        st.metric(
            "Partially Paid",
            statistics["partially_paid"]
        )


    with col5:

        st.metric(
            "Overdue",
            statistics["overdue"]
        )


    st.divider()

    payments = get_all_payments()


# ==================================================
# RECORD PAYMENT
# ==================================================

def show_record_payment():

    st.subheader("💰 Record Payment")

    payments = get_all_payments()

    if not payments:

        st.info(
            "No payment records are available."
        )

        return


    # ==============================================
    # ONLY SHOW UNPAID PAYMENTS
    # ==============================================

    unpaid_payments = [

        payment

        for payment in payments

        if payment.payment_status != "Paid"

    ]


    if not unpaid_payments:

        st.success(
            "🎉 All invoices are fully paid."
        )

        return


    # ==============================================
    # PAYMENT SELECTION
    # ==============================================

    payment_options = {}

    for payment in unpaid_payments:

        site_name = (
            payment.site.name
            if payment.site
            else "Unknown Site"
        )

        remaining = (
            float(payment.total_amount or 0)
            -
            float(payment.paid_amount or 0)
        )

        label = (
            f"{payment.invoice_number} | "
            f"{site_name} | "
            f"Balance: ₹ {remaining:,.2f}"
        )

        payment_options[label] = payment


    selected_label = st.selectbox(
        "Select Invoice",
        list(payment_options.keys())
    )


    payment = payment_options[
        selected_label
    ]


    # ==============================================
    # PAYMENT SUMMARY
    # ==============================================

    total_amount = float(
        payment.total_amount or 0
    )

    paid_amount = float(
        payment.paid_amount or 0
    )

    remaining_amount = (
        total_amount - paid_amount
    )


    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Invoice Amount",
            f"₹ {total_amount:,.2f}"
        )

    with col2:

        st.metric(
            "Already Paid",
            f"₹ {paid_amount:,.2f}"
        )

    with col3:

        st.metric(
            "Remaining Balance",
            f"₹ {remaining_amount:,.2f}"
        )


    st.divider()


    # ==============================================
    # PAYMENT FORM
    # ==============================================

    with st.form(
        f"record_payment_form_{payment.id}"
    ):

        col1, col2 = st.columns(2)


        with col1:

            amount = st.number_input(
                "Payment Amount (₹) *",
                min_value=0.01,
                max_value=float(remaining_amount),
                value=float(remaining_amount),
                step=100.0
            )


        with col2:

            paid_date = st.date_input(
                "Payment Date *",
                value=date.today()
            )


        col1, col2 = st.columns(2)


        with col1:

            payment_mode = st.selectbox(
                "Payment Mode *",
                [
                    "Cash",
                    "UPI",
                    "Bank Transfer",
                    "Cheque",
                    "Card",
                    "Other"
                ]
            )


        with col2:

            transaction_reference = st.text_input(
                "Transaction / Reference Number"
            )


        remarks = st.text_area(
            "Remarks"
        )


        submitted = st.form_submit_button(
            "💾 Record Payment",
            use_container_width=True
        )


        if submitted:

            try:

                record_payment(
                    payment_id=payment.id,
                    amount=amount,
                    payment_date=paid_date,
                    payment_mode=payment_mode,
                    transaction_reference=transaction_reference,
                    remarks=remarks
                )

                st.success(
                    "Payment recorded successfully."
                )

                st.rerun()


            except ValueError as e:

                st.error(
                    str(e)
                )


            except Exception as e:

                st.error(
                    f"Error recording payment: {e}"
                )

