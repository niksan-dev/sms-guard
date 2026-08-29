import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path
from services.email_service import (
    send_email_with_pdf,
)
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
from services.company_settings_service import get_company_settings

from services.pdf_service import (
    generate_guard_salary_pdf,
)

from services.site_invoice_template_service import (
    list_site_invoice_templates,
    get_default_site_invoice_template,
    generate_site_bill_pdf_from_template,
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
# COMPANY SETTINGS CHECK
# ============================================================

def _require_company_settings_for_invoice() -> bool:
    """Stop site billing generation until company settings exist."""

    try:
        settings = get_company_settings()
    except Exception as error:
        st.error(
            f"Unable to load company settings: {error}"
        )
        return False

    if settings is not None:
        return True

    st.warning(
        "⚠️ Company settings are not configured. "
        "Please configure your company details before generating an invoice."
    )

    st.markdown(
        "Configure the company name, logo, address, contact number, "
        "PAN/GST and bank details in **Company Settings**."
    )

    # If Company Settings is a Streamlit multipage script, open it directly.
    # Otherwise leave navigation to the application's existing sidebar/router.
    project_root = Path(__file__).resolve().parents[1]
    page_candidates = [
        project_root / "pages" / "company_settings.py",
        project_root / "pages" / "company_settings_page.py",
    ]

    existing_page = next(
        (path for path in page_candidates if path.exists()),
        None,
    )

    if existing_page is not None:
        try:
            st.page_link(
                str(existing_page.relative_to(project_root)),
                label="⚙️ Configure Company Settings",
                icon="⚙️",
            )
        except Exception:
            if st.button(
                "⚙️ Configure Company Settings",
                type="primary",
                width="stretch",
                key="configure_company_settings",
            ):
                st.switch_page(
                    str(existing_page.relative_to(project_root))
                )
    else:
        st.info(
            "Open **Company Settings** from the sidebar, save the company "
            "details, then return here to generate the invoice."
        )

    return False


# ============================================================
# SITE BILLS
# ============================================================

def show_site_bills():

    st.subheader("🏢 Site Billing")

    if not _require_company_settings_for_invoice():
        return

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
    # INVOICE TEMPLATE
    # --------------------------------------------------------
    templates = list_site_invoice_templates()

    if not templates:
        st.error(
            "No site invoice templates found. "
            "Add an .xlsx template under templates/site_invoice/."
        )
        return

    template_names = list(templates.keys())
    default_path = get_default_site_invoice_template()
    default_name = default_path.stem
    default_index = (
        template_names.index(default_name)
        if default_name in template_names
        else 0
    )

    selected_template_name = st.selectbox(
        "Invoice Template",
        options=template_names,
        index=default_index,
        key="billing_site_invoice_template"
    )

    selected_template_path = templates[
        selected_template_name
    ]

    st.caption(
        f"Template: {selected_template_path.name}"
    )

    st.session_state[
        "site_invoice_template_path"
    ] = str(selected_template_path)

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

        # GST rates are controlled centrally from Company Settings.
        # They are NOT editable from the Site Bill page.

        company_settings = get_company_settings()

        if company_settings is None:

            st.warning(
                "Company Settings are not configured."
            )

            return

        cgst_rate = float(
            company_settings.cgst_rate
            if company_settings.cgst_rate is not None
            else 9.0
        )

        sgst_rate = float(
            company_settings.sgst_rate
            if company_settings.sgst_rate is not None
            else 9.0
        )

        st.info(
            f"GST Rates from Company Settings: "
            f"CGST {cgst_rate:.2f}% | "
            f"SGST {sgst_rate:.2f}%"
        )

        # ----------------------------------------------------
        # GST CALCULATION
        # ----------------------------------------------------

        gross_amount = float(
            data["gross_amount"] or 0
        )

        cgst_amount = round(
            gross_amount
            * cgst_rate
            / 100,
            2
        )

        sgst_amount = round(
            gross_amount
            * sgst_rate
            / 100,
            2
        )

        total_amount = round(
            gross_amount
            + cgst_amount
            + sgst_amount,
            2
        )

        # ----------------------------------------------------
        # TAX SUMMARY
        # ----------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Gross",
                format_currency(
                    gross_amount
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
                month=int(selected_month)
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
        bill,
        template_path=selected_template_path
    )


# ============================================================
# SITE BILL ACTIONS
# ============================================================

def show_site_bill_actions(
    bill,
    template_path=None
):

    if template_path is None:
        template_path = st.session_state.get(
            "site_invoice_template_path"
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(
            "👁 View",
            width="stretch",
            key=f"view_bill_{bill.id}"
        ):
            st.session_state["view_site_bill_id"] = bill.id

    with col2:
        pdf_data = build_site_pdf_from_bill(
            bill,
            template_path=template_path
        )
        st.download_button(
            "📄 Export PDF",
            data=pdf_data,
            file_name=f"{bill.bill_number}.pdf",
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
            st.session_state["print_site_bill_id"] = bill.id

    with col4:
        if st.button(
            "📧 Send Email",
            width="stretch",
            key=f"email_site_bill_{bill.id}"
        ):
            st.session_state["email_site_bill_id"] = bill.id

    if st.session_state.get("email_site_bill_id") == bill.id:
        st.markdown("### 📧 Send Site Bill")

        recipient_email = st.text_input(
            "Site Billing Email",
            value=getattr(bill.site, "email", "") or "",
            key=f"site_email_{bill.id}",
            placeholder="accounts@client.com"
        )

        if st.button(
            "Send Site Bill",
            type="primary",
            key=f"send_site_bill_{bill.id}"
        ):
            pdf_data = build_site_pdf_from_bill(
                bill,
                template_path=template_path
            )

            subject = (
                f"Security Service Bill - {bill.site.site_code} - "
                f"{month_name(bill.billing_month)} {bill.billing_year}"
            )

            body = f"""Dear Sir/Madam,

Please find attached the security service bill.

Site: {bill.site.site_code} - {bill.site.name}
Billing Month: {month_name(bill.billing_month)} {bill.billing_year}
Bill Number: {bill.bill_number}

Gross Amount: {format_currency(bill.gross_amount)}
CGST: {format_currency(bill.cgst_amount)}
SGST: {format_currency(bill.sgst_amount)}
Grand Total: {format_currency(bill.total_amount)}

Regards,
Security Management System
"""

            success, message = send_email_with_pdf(
                recipient_email=recipient_email,
                subject=subject,
                body=body,
                pdf_data=pdf_data,
                pdf_filename=f"{bill.bill_number}.pdf"
            )

            if success:
                st.success(message)
            else:
                st.error(message)

    if st.session_state.get("view_site_bill_id") == bill.id:
        show_site_bill_preview(bill)

    if st.session_state.get("print_site_bill_id") == bill.id:
        show_print_button(
            "site",
            bill,
            template_path=template_path
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


def build_site_pdf_from_bill(
    bill,
    template_path=None
):

    if template_path is None:
        template_path = st.session_state.get(
            "site_invoice_template_path"
        )

    return generate_site_bill_pdf_from_template(
        bill,
        template_path=template_path
    )


# ============================================================
# PRINT
# ============================================================

def show_print_button(
    document_type,
    document,
    template_path=None
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