import streamlit as st
import pandas as pd
from datetime import date

from services.guard_salary_service import (
    get_guard_salary_data,
    create_guard_salary_slip,
    get_guard_salary_slip,
    get_monthly_salary_slips,
)

from services.site_bill_service import (
    get_site_bill_data,
    create_site_bill,
    get_site_bill,
    get_monthly_site_bills,
)

from services.guard_service import get_all_guards
from services.site_service import get_all_sites

from services.pdf_service import (
    generate_guard_salary_pdf,
    generate_site_bill_pdf,
)


# ============================================================
# HELPERS
# ============================================================

def format_currency(value):

    try:
        return f"₹ {float(value or 0):,.2f}"

    except (TypeError, ValueError):
        return "₹ 0.00"


def month_name(month):

    return date(
        2000,
        int(month),
        1
    ).strftime("%B")


def get_active_guards():

    guards = get_all_guards()

    return [
        guard
        for guard in guards
        if (guard.status or "").lower()
        == "active"
    ]


def get_active_sites():

    sites = get_all_sites()

    return [
        site
        for site in sites
        if (site.status or "").lower()
        == "active"
    ]


# ============================================================
# MAIN PAGE
# ============================================================

def show_billing_payroll():

    st.title("💰 Billing & Payroll")

    st.caption(
        "Generate, view, print and export site bills "
        "and guard salary slips."
    )

    st.divider()

    site_tab, guard_tab = st.tabs([
        "🏢 Site Bills",
        "👮 Guard Salary"
    ])

    with site_tab:

        show_site_bills()

    with guard_tab:

        show_guard_salary()


# ============================================================
# SITE BILLS
# ============================================================

def show_site_bills():

    st.subheader("🏢 Site Billing")

    col1, col2 = st.columns(2)

    with col1:

        selected_month = st.selectbox(
            "Billing Month",
            options=list(range(1, 13)),
            index=date.today().month - 1,
            format_func=month_name,
            key="billing_site_month"
        )

    with col2:

        selected_year = st.number_input(
            "Billing Year",
            min_value=2020,
            max_value=2100,
            value=date.today().year,
            step=1,
            key="billing_site_year"
        )

    sites = get_active_sites()

    if not sites:

        st.warning(
            "No active sites available."
        )

        return

    site_map = {
        f"{site.site_code} - {site.name}": site
        for site in sites
    }

    st.markdown("### Generate Site Bill")

    selected_site_label = st.selectbox(
        "Select Site",
        options=list(site_map.keys()),
        key="billing_site_selection"
    )

    selected_site = site_map[
        selected_site_label
    ]

    # --------------------------------------------------------
    # PREVIEW CALCULATION
    # --------------------------------------------------------

    data = get_site_bill_data(
        selected_site.id,
        int(selected_year),
        int(selected_month)
    )

    if not data:

        st.info(
            "No recorded guard shifts found for "
            "this site in the selected month."
        )

    else:

        st.markdown("### Bill Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Shift 1",
                data["shift_1_count"]
            )

        with col2:

            st.metric(
                "Shift 2",
                data["shift_2_count"]
            )

        with col3:

            st.metric(
                "Total Shifts",
                data["total_shifts"]
            )

        with col4:

            st.metric(
                "Gross Amount",
                format_currency(
                    data["gross_amount"]
                )
            )

        st.divider()

        # ----------------------------------------------------
        # GST
        # ----------------------------------------------------

        st.markdown("### Tax")

        col1, col2 = st.columns(2)

        with col1:

            cgst_rate = st.number_input(
                "CGST %",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.5,
                key="site_cgst"
            )

        with col2:

            sgst_rate = st.number_input(
                "SGST %",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.5,
                key="site_sgst"
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

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Gross",
                format_currency(
                    data["gross_amount"]
                )
            )

        with col2:

            st.metric(
                "GST",
                format_currency(
                    cgst_amount
                    + sgst_amount
                )
            )

        with col3:

            st.metric(
                "Grand Total",
                format_currency(
                    total_amount
                )
            )

        # ----------------------------------------------------
        # GENERATE
        # ----------------------------------------------------

        if st.button(
            "📄 Generate / Update Bill",
            type="primary",
            width="stretch",
            key="generate_site_bill"
        ):

            success, message, bill = create_site_bill(
                site_id=selected_site.id,
                year=int(selected_year),
                month=int(selected_month),
                cgst_rate=float(cgst_rate),
                sgst_rate=float(sgst_rate)
            )

            if success:

                st.success(message)

                st.rerun()

            else:

                st.error(message)

    st.divider()

    # --------------------------------------------------------
    # SAVED BILL
    # --------------------------------------------------------

    st.subheader("📋 Saved Bill")

    bill = get_site_bill(
        selected_site.id,
        int(selected_year),
        int(selected_month)
    )

    if not bill:

        st.info(
            "No saved bill exists for this site/month."
        )

        return

    show_site_bill_actions(
        bill
    )


# ============================================================
# SITE BILL ACTIONS
# ============================================================

def show_site_bill_actions(bill):

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "👁 View",
            width="stretch",
            key=f"view_bill_{bill.id}"
        ):

            st.session_state[
                "view_site_bill_id"
            ] = bill.id

    with col2:

        pdf_data = build_site_pdf_from_bill(
            bill
        )

        st.download_button(
            "📄 Export PDF",
            data=pdf_data,
            file_name=(
                f"{bill.bill_number}.pdf"
            ),
            mime="application/pdf",
            width="stretch",
            key=f"export_bill_{bill.id}"
        )

    with col3:

        if st.button(
            "🖨 Print",
            width="stretch",
            key=f"print_bill_{bill.id}"
        ):

            st.session_state[
                "print_site_bill_id"
            ] = bill.id

    if st.session_state.get(
        "view_site_bill_id"
    ) == bill.id:

        show_site_bill_preview(
            bill
        )

    if st.session_state.get(
        "print_site_bill_id"
    ) == bill.id:

        show_print_button(
            "site",
            bill
        )


# ============================================================
# SITE BILL PREVIEW
# ============================================================

def show_site_bill_preview(bill):

    st.markdown("### 👁 Bill Preview")

    st.info(
        f"Invoice: {bill.bill_number}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write(
            f"**Site:** "
            f"{bill.site.site_code}"
        )

    with col2:

        st.write(
            f"**Name:** "
            f"{bill.site.name}"
        )

    with col3:

        st.write(
            f"**Month:** "
            f"{month_name(bill.billing_month)} "
            f"{bill.billing_year}"
        )

    st.divider()

    table = pd.DataFrame([
        {
            "Particular": "Security Guard Service",
            "Shift": "Shift 1",
            "Guards": bill.shift_1_count,
            "Days": bill.total_days,
            "Rate": format_currency(
                bill.shift_rate
            ),
            "Amount": format_currency(
                bill.shift_rate
                * bill.shift_1_count
            )
        },
        {
            "Particular": "Security Guard Service",
            "Shift": "Shift 2",
            "Guards": bill.shift_2_count,
            "Days": bill.total_days,
            "Rate": format_currency(
                bill.shift_rate
            ),
            "Amount": format_currency(
                bill.shift_rate
                * bill.shift_2_count
            )
        }
    ])

    st.dataframe(
        table,
        width="stretch",
        hide_index=True
    )

    st.markdown(
        f"""
        **Gross Amount:** {format_currency(bill.gross_amount)}

        **CGST:** {format_currency(bill.cgst_amount)}

        **SGST:** {format_currency(bill.sgst_amount)}

        ### Grand Total: {format_currency(bill.total_amount)}
        """
    )


# ============================================================
# GUARD SALARY
# ============================================================

def show_guard_salary():

    st.subheader("👮 Guard Salary")

    col1, col2 = st.columns(2)

    with col1:

        selected_month = st.selectbox(
            "Salary Month",
            options=list(range(1, 13)),
            index=date.today().month - 1,
            format_func=month_name,
            key="billing_guard_month"
        )

    with col2:

        selected_year = st.number_input(
            "Salary Year",
            min_value=2020,
            max_value=2100,
            value=date.today().year,
            step=1,
            key="billing_guard_year"
        )

    guards = get_active_guards()

    if not guards:

        st.warning(
            "No active guards available."
        )

        return

    guard_map = {
        f"{guard.employee_id} - {guard.name}": guard
        for guard in guards
    }

    st.markdown("### Generate Salary Slip")

    selected_guard_label = st.selectbox(
        "Select Guard",
        options=list(guard_map.keys()),
        key="billing_guard_selection"
    )

    selected_guard = guard_map[
        selected_guard_label
    ]

    data = get_guard_salary_data(
        selected_guard.id,
        int(selected_year),
        int(selected_month)
    )

    if not data:

        st.info(
            "No work records found for this guard "
            "in the selected month."
        )

    else:

        st.markdown("### Salary Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Shift 1",
                data["shift_1_count"]
            )

        with col2:

            st.metric(
                "Shift 2",
                data["shift_2_count"]
            )

        with col3:

            st.metric(
                "Total Shifts",
                data["total_shifts"]
            )

        with col4:

            st.metric(
                "Gross Salary",
                format_currency(
                    data["gross_salary"]
                )
            )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Monthly Salary",
                format_currency(
                    data["monthly_salary"]
                )
            )

        with col2:

            st.metric(
                "Total Advance",
                format_currency(
                    data["total_advance"]
                )
            )

        with col3:

            st.metric(
                "Net Payable",
                format_currency(
                    data["net_payable"]
                )
            )

        st.divider()

        # ----------------------------------------------------
        # ADVANCES
        # ----------------------------------------------------

        st.markdown("### Advances")

        if data["advances"]:

            advance_data = []

            for advance in data["advances"]:

                advance_data.append({

                    "Date":
                        advance.record_date,

                    "Category":
                        advance.category,

                    "Description":
                        advance.description or "-",

                    "Amount":
                        format_currency(
                            advance.amount
                        )
                })

            st.dataframe(
                pd.DataFrame(
                    advance_data
                ),
                width="stretch",
                hide_index=True
            )

        else:

            st.info(
                "No advances recorded."
            )

        # ----------------------------------------------------
        # GENERATE
        # ----------------------------------------------------

        if st.button(
            "📄 Generate / Update Salary Slip",
            type="primary",
            width="stretch",
            key="generate_salary_slip"
        ):

            success, message, slip = (
                create_guard_salary_slip(
                    guard_id=selected_guard.id,
                    year=int(selected_year),
                    month=int(selected_month)
                )
            )

            if success:

                st.success(message)

                st.rerun()

            else:

                st.error(message)

    st.divider()

    # --------------------------------------------------------
    # SAVED SLIP
    # --------------------------------------------------------

    st.subheader("📋 Saved Salary Slip")

    slip = get_guard_salary_slip(
        selected_guard.id,
        int(selected_year),
        int(selected_month)
    )

    if not slip:

        st.info(
            "No saved salary slip exists "
            "for this guard/month."
        )

        return

    show_salary_slip_actions(
        slip
    )


# ============================================================
# SALARY SLIP ACTIONS
# ============================================================

def show_salary_slip_actions(slip):

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "👁 View",
            width="stretch",
            key=f"view_slip_{slip.id}"
        ):

            st.session_state[
                "view_salary_slip_id"
            ] = slip.id

    with col2:

        pdf_data = build_salary_pdf_from_slip(
            slip
        )

        st.download_button(
            "📄 Export PDF",
            data=pdf_data,
            file_name=(
                f"{slip.slip_number}.pdf"
            ),
            mime="application/pdf",
            width="stretch",
            key=f"export_slip_{slip.id}"
        )

    with col3:

        if st.button(
            "🖨 Print",
            width="stretch",
            key=f"print_slip_{slip.id}"
        ):

            st.session_state[
                "print_salary_slip_id"
            ] = slip.id

    if st.session_state.get(
        "view_salary_slip_id"
    ) == slip.id:

        show_salary_slip_preview(
            slip
        )

    if st.session_state.get(
        "print_salary_slip_id"
    ) == slip.id:

        show_print_button(
            "salary",
            slip
        )


# ============================================================
# SALARY SLIP PREVIEW
# ============================================================

def show_salary_slip_preview(slip):

    st.markdown("### 👁 Salary Slip Preview")

    st.info(
        f"Slip: {slip.slip_number}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write(
            f"**Employee ID:** "
            f"{slip.guard.employee_id}"
        )

    with col2:

        st.write(
            f"**Guard:** "
            f"{slip.guard.name}"
        )

    with col3:

        st.write(
            f"**Month:** "
            f"{month_name(slip.salary_month)} "
            f"{slip.salary_year}"
        )

    st.divider()

    earnings = pd.DataFrame([
        {
            "Description": "Monthly Salary",
            "Amount": format_currency(
                slip.monthly_salary
            )
        },
        {
            "Description": "Salary Per Shift",
            "Amount": format_currency(
                slip.shift_rate
            )
        },
        {
            "Description": "Shift 1",
            "Amount": slip.shift_1_count
        },
        {
            "Description": "Shift 2",
            "Amount": slip.shift_2_count
        },
        {
            "Description": "Total Shifts",
            "Amount": slip.total_shifts
        },
        {
            "Description": "Gross Salary",
            "Amount": format_currency(
                slip.gross_salary
            )
        }
    ])

    st.markdown("#### Earnings")

    st.dataframe(
        earnings,
        width="stretch",
        hide_index=True
    )

    st.markdown("#### Advances")

    data = get_guard_salary_data(
        slip.guard_id,
        slip.salary_year,
        slip.salary_month
    )

    if data and data["advances"]:

        advances = pd.DataFrame([
            {
                "Date": advance.record_date,
                "Category": advance.category,
                "Description":
                    advance.description or "-",
                "Amount":
                    format_currency(
                        advance.amount
                    )
            }
            for advance in data["advances"]
        ])

        st.dataframe(
            advances,
            width="stretch",
            hide_index=True
        )

    else:

        st.info(
            "No advances."
        )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Gross Salary",
            format_currency(
                slip.gross_salary
            )
        )

    with col2:

        st.metric(
            "Total Advance",
            format_currency(
                slip.total_advance
            )
        )

    with col3:

        st.metric(
            "Net Payable",
            format_currency(
                slip.net_payable
            )
        )


# ============================================================
# PDF BUILDERS
# ============================================================

def build_salary_pdf_from_slip(slip):

    data = get_guard_salary_data(
        slip.guard_id,
        slip.salary_year,
        slip.salary_month
    )

    if not data:
        return b""

    data["slip_number"] = (
        slip.slip_number
    )

    return generate_guard_salary_pdf(
        data
    )


def build_site_pdf_from_bill(bill):

    data = get_site_bill_data(
        bill.site_id,
        bill.billing_year,
        bill.billing_month
    )

    if not data:
        return b""

    data["bill_number"] = (
        bill.bill_number
    )

    data["cgst_amount"] = (
        bill.cgst_amount
    )

    data["sgst_amount"] = (
        bill.sgst_amount
    )

    data["total_amount"] = (
        bill.total_amount
    )

    return generate_site_bill_pdf(
        data
    )


# ============================================================
# PRINT
# ============================================================

def show_print_button(
    document_type,
    document
):

    if document_type == "salary":

        pdf_data = build_salary_pdf_from_slip(
            document
        )

    else:

        pdf_data = build_site_pdf_from_bill(
            document
        )

    st.info(
        "Use your browser's print dialog "
        "after opening the generated PDF."
    )

    st.download_button(
        "🖨 Open PDF for Printing",
        data=pdf_data,
        file_name=(
            f"{document.slip_number}.pdf"
            if document_type == "salary"
            else f"{document.bill_number}.pdf"
        ),
        mime="application/pdf",
        width="stretch",
        key=(
            f"print_pdf_{document_type}_"
            f"{document.id}"
        )
    )