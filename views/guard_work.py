import streamlit as st
import pandas as pd
import calendar

from datetime import date

from services.guard_daily_work_service import (
    create_guard_daily_work,
    get_daily_work_records,
    delete_daily_work,
    get_daily_work_summary,
    get_guard_daily_attendance,
    get_guard_monthly_attendance,
    get_site_daily_attendance,
    get_site_monthly_attendance,
)

from services.guard_service import get_all_guards
from services.site_service import get_all_sites


# ==================================================
# HELPERS
# ==================================================

def get_active_guards():

    guards = get_all_guards()

    return [
        guard
        for guard in guards
        if (guard.status or "").lower() == "active"
    ]


def get_active_sites():

    sites = get_all_sites()

    return [
        site
        for site in sites
        if (site.status or "").lower() == "active"
    ]


def format_shift(shift_number):

    try:
        return f"Shift {int(shift_number)}"

    except (TypeError, ValueError):
        return "-"


def format_currency(value):

    try:
        return f"₹ {float(value or 0):,.2f}"

    except (TypeError, ValueError):
        return "₹ 0.00"

def build_guard_shift_table(attendance):

    grouped_data = {}

    for item in attendance:

        guard_id = item.get("guard_id")

        if guard_id is None:
            guard_id = item.get(
                "employee_id",
                item.get("guard_name", "unknown")
            )

        if guard_id not in grouped_data:

            grouped_data[guard_id] = {

                "Employee ID": item.get(
                    "employee_id",
                    "-"
                ),

                "Guard Name": item.get(
                    "guard_name",
                    "Unknown Guard"
                ),

                "Shift 1": "N/A",

                "Shift 2": "N/A",

                "Total Shifts": 0,

                "Total Days": item.get(
                    "total_days",
                    "-"
                ),

                "Monthly Salary": float(
                    item.get(
                        "monthly_salary",
                        0
                    ) or 0
                ),

                "Shift Rate": 0,

                "Actual Salary": 0
            }

        shift_number = item.get(
            "shift_number"
        )

        site_code = item.get(
            "site_code",
            "-"
        )

        site_name = item.get(
            "site_name",
            ""
        )

        site_value = site_code

        if site_name:
            site_value = (
                f"{site_code} - {site_name}"
            )

        if is_present(
            item.get("status")
        ):

            if shift_number == 1:

                grouped_data[guard_id][
                    "Shift 1"
                ] = site_value

            elif shift_number == 2:

                grouped_data[guard_id][
                    "Shift 2"
                ] = site_value

            grouped_data[guard_id][
                "Total Shifts"
            ] += 1

            grouped_data[guard_id][
                "Actual Salary"
            ] += float(
                item.get(
                    "actual_salary",
                    0
                ) or 0
            )

        item_shift_rate = float(
            item.get(
                "shift_rate",
                0
            ) or 0
        )

        if item_shift_rate > 0:

            grouped_data[guard_id][
                "Shift Rate"
            ] = item_shift_rate

    table_data = []

    for row in grouped_data.values():

        row["Monthly Salary"] = format_currency(
            row["Monthly Salary"]
        )

        row["Shift Rate"] = format_currency(
            row["Shift Rate"]
        )

        row["Actual Salary"] = format_currency(
            row["Actual Salary"]
        )

        table_data.append(row)

    return pd.DataFrame(table_data)


def build_site_shift_table(attendance):
    """
    Build one row per site.

    Shift 1 and Shift 2 contain the number of PRESENT guards
    recorded for that site and shift.
    """

    grouped_data = {}

    for item in attendance:

        site_id = item.get("site_id")

        if site_id is None:
            site_id = item.get(
                "site_code",
                item.get("site_name", "unknown")
            )

        if site_id not in grouped_data:

            site_code = item.get(
                "site_code",
                "-"
            )

            site_name = item.get(
                "site_name",
                "Unknown Site"
            )

            site_value = site_code

            if site_name:
                site_value = (
                    f"{site_code} - {site_name}"
                )

            grouped_data[site_id] = {

                "Site": site_value,

                "Shift 1": 0,

                "Shift 2": 0,

                "Total Shifts": 0,

                "Total Days": item.get(
                    "total_days",
                    "-"
                ),

                "Monthly Rate": float(
                    item.get(
                        "guard_rate",
                        0
                    ) or 0
                ),

                "Shift Rate": 0,

                "Actual Revenue": 0
            }

        if not is_present(
            item.get("status")
        ):
            continue

        shift_number = item.get(
            "shift_number"
        )

        if shift_number == 1:

            grouped_data[site_id][
                "Shift 1"
            ] += 1

        elif shift_number == 2:

            grouped_data[site_id][
                "Shift 2"
            ] += 1

        else:
            continue

        grouped_data[site_id][
            "Total Shifts"
        ] += 1

        grouped_data[site_id][
            "Actual Revenue"
        ] += float(
            item.get(
                "actual_revenue",
                0
            ) or 0
        )

        item_shift_rate = float(
            item.get(
                "shift_rate",
                0
            ) or 0
        )

        if item_shift_rate > 0:

            grouped_data[site_id][
                "Shift Rate"
            ] = item_shift_rate

    table_data = []

    for row in grouped_data.values():

        row["Monthly Rate"] = format_currency(
            row["Monthly Rate"]
        )

        row["Shift Rate"] = format_currency(
            row["Shift Rate"]
        )

        row["Actual Revenue"] = format_currency(
            row["Actual Revenue"]
        )

        table_data.append(row)

    return pd.DataFrame(table_data)


def get_days_in_month(year, month):

    return calendar.monthrange(
        int(year),
        int(month)
    )[1]


# ==================================================
# GUARD SALARY CALCULATION
#
# Example:
#
# Monthly Salary = 15,000
# Days in Month = 30
# Shift Rate     = 15,000 / 30 = 500
#
# 45 Shifts:
# Final Salary   = 500 × 45 = 22,500
# ==================================================

def calculate_guard_salary(
    monthly_salary,
    total_shifts,
    year,
    month
):

    days_in_month = get_days_in_month(
        year,
        month
    )

    monthly_salary = float(
        monthly_salary or 0
    )

    total_shifts = int(
        total_shifts or 0
    )

    shift_rate = (
        monthly_salary / days_in_month
        if days_in_month > 0
        else 0
    )

    final_salary = (
        shift_rate * total_shifts
    )

    return {
        "days_in_month": days_in_month,
        "monthly_salary": monthly_salary,
        "shift_rate": shift_rate,
        "total_shifts": total_shifts,
        "final_salary": final_salary
    }


# ==================================================
# SITE REVENUE CALCULATION
#
# Site Guard Rate is treated as monthly amount.
#
# Example:
#
# Monthly Rate = 18,000
# Days = 30
# Shift Rate = 18,000 / 30 = 600
#
# 45 completed shifts:
# Revenue = 600 × 45 = 27,000
# ==================================================

def calculate_site_revenue(
    monthly_rate,
    total_shifts,
    year,
    month
):

    days_in_month = get_days_in_month(
        year,
        month
    )

    monthly_rate = float(
        monthly_rate or 0
    )

    total_shifts = int(
        total_shifts or 0
    )

    shift_rate = (
        monthly_rate / days_in_month
        if days_in_month > 0
        else 0
    )

    final_revenue = (
        shift_rate * total_shifts
    )

    return {
        "days_in_month": days_in_month,
        "monthly_rate": monthly_rate,
        "shift_rate": shift_rate,
        "total_shifts": total_shifts,
        "final_revenue": final_revenue
    }


def is_present(status):

    return str(
        status or ""
    ).strip().lower() == "present"


# ==================================================
# MAIN PAGE
# ==================================================

def show_guard_work():

    st.title("👮 Guard Work Management")

    st.caption(
        "Record daily guard shifts and monitor guard attendance, "
        "salary and site revenue."
    )

    st.divider()

    tab1, tab2, tab3 = st.tabs([
        "📝 Record Work",
        "👮 Guard Attendance",
        "🏢 Site Attendance"
    ])

    with tab1:
        show_record_work_tab()

    with tab2:
        show_guard_attendance_tab()

    with tab3:
        show_site_attendance_tab()


# ==================================================
# TAB 1 - RECORD WORK
# ==================================================

def show_record_work_tab():

    selected_date = st.date_input(
        "Work Date",
        value=date.today(),
        key="work_date"
    )

    guards = get_active_guards()
    sites = get_active_sites()

    if not guards:

        st.warning(
            "No active guards available."
        )

        return

    if not sites:

        st.warning(
            "No active sites available."
        )

        return

    st.subheader(
        "📝 Record Guard Shift"
    )

    guard_map = {
        f"{guard.name} ({guard.employee_id})": guard
        for guard in guards
    }

    site_map = {
        f"{site.site_code} - {site.name}": site
        for site in sites
    }

    col1, col2 = st.columns(2)

    with col1:

        selected_guard_label = st.selectbox(
            "Select Guard",
            options=list(guard_map.keys()),
            key="selected_guard"
        )

        selected_guard = guard_map[
            selected_guard_label
        ]

    with col2:

        selected_site_label = st.selectbox(
            "Select Site",
            options=list(site_map.keys()),
            key="selected_site"
        )

        selected_site = site_map[
            selected_site_label
        ]

    col1, col2 = st.columns(2)

    with col1:

        shift_number = st.radio(
            "Select Shift",
            options=[1, 2],
            horizontal=True,
            format_func=format_shift,
            key="shift_number"
        )

    with col2:

        status = st.selectbox(
            "Status",
            options=[
                "Present",
                "Absent"
            ],
            index=0,
            key="work_status"
        )

    if st.button(
        "➕ Record Shift",
        type="primary",
        width="stretch"
    ):

        success, message = create_guard_daily_work(
            guard_id=selected_guard.id,
            site_id=selected_site.id,
            work_date=selected_date,
            shift_number=shift_number,
            status=status
        )

        if success:

            st.success(message)
            st.rerun()

        else:

            st.error(message)

    st.divider()

    show_daily_work_records(
        selected_date
    )


# ==================================================
# RECORDED SHIFTS
# ==================================================

def show_daily_work_records(selected_date):

    records = get_daily_work_records(
        selected_date
    )

    st.subheader(
        "📋 Recorded Shifts"
    )

    if not records:

        st.info(
            "No shifts recorded for this date."
        )

        return

    # ==============================================
    # SUMMARY
    # ==============================================

    summary = get_daily_work_summary(
        selected_date
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Shifts",
            summary.get(
                "total_shifts",
                0
            )
        )

    with col2:

        st.metric(
            "Shift 1",
            summary.get(
                "shift_1_count",
                0
            )
        )

    with col3:

        st.metric(
            "Shift 2",
            summary.get(
                "shift_2_count",
                0
            )
        )

    with col4:

        st.metric(
            "Unique Guards",
            summary.get(
                "unique_guards",
                0
            )
        )

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    # ==============================================
    # TABLE
    # ==============================================

    table_data = []

    for record in records:

        guard_name = (
            record.guard.name
            if record.guard
            else "Unknown Guard"
        )

        employee_id = (
            record.guard.employee_id
            if record.guard
            else "-"
        )

        site_name = (
            record.site.name
            if record.site
            else "Unknown Site"
        )

        site_code = (
            record.site.site_code
            if record.site
            else "-"
        )

        table_data.append({

            "ID": record.id,

            "Employee ID": employee_id,

            "Guard": guard_name,

            "Site": (
                f"{site_code} - {site_name}"
            ),

            "Shift": format_shift(
                record.shift_number
            ),

            "Status": (
                record.status or "Present"
            )
        })

    df = pd.DataFrame(
        table_data
    )

    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
        column_config={

            "ID": st.column_config.NumberColumn(
                "ID",
                width="small"
            ),

            "Employee ID": st.column_config.TextColumn(
                "Employee ID",
                width="medium"
            ),

            "Guard": st.column_config.TextColumn(
                "Guard",
                width="medium"
            ),

            "Site": st.column_config.TextColumn(
                "Site",
                width="large"
            ),

            "Shift": st.column_config.TextColumn(
                "Shift",
                width="small"
            ),

            "Status": st.column_config.TextColumn(
                "Status",
                width="small"
            )
        }
    )

    # ==============================================
    # DELETE SHIFT
    # ==============================================

    st.markdown(
        "### 🗑 Delete a recorded shift"
    )

    delete_options = {

        (
            f"{record.id} - "
            f"{record.guard.name if record.guard else 'Unknown Guard'} - "
            f"{record.site.site_code if record.site else 'Unknown Site'} - "
            f"Shift {record.shift_number}"
        ): record.id

        for record in records
    }

    col1, col2 = st.columns(
        [3, 1],
        vertical_alignment="bottom"
    )

    with col1:

        selected_delete_label = st.selectbox(
            "Select shift to delete",
            options=list(
                delete_options.keys()
            ),
            key="delete_shift_select"
        )

    with col2:

        if st.button(
            "🗑 Delete",
            type="secondary",
            width="stretch",
            key="delete_selected_shift"
        ):

            record_id = delete_options[
                selected_delete_label
            ]

            success, message = delete_daily_work(
                record_id
            )

            if success:

                st.success(message)
                st.rerun()

            else:

                st.error(message)


# ==================================================
# TAB 2 - GUARD ATTENDANCE
# ==================================================

def show_guard_attendance_tab():

    daily_tab, monthly_tab = st.tabs([
        "📅 Daily Records",
        "📊 Monthly Records"
    ])

    # ==============================================
    # DAILY GUARD RECORDS
    # ==============================================

    with daily_tab:

        selected_date = st.date_input(
            "Select Date",
            value=date.today(),
            key="guard_daily_attendance_date"
        )

        attendance = get_guard_daily_attendance(
            selected_date
        )

        st.subheader(
            "👮 Daily Guard Attendance"
        )

        if not attendance:

            st.info(
                "No guard attendance records found for this date."
            )

        else:

            df = pd.DataFrame(
                attendance
            )

            # ======================================
            # CALCULATE DAILY SALARY
            # ONE PRESENT SHIFT = ONE SHIFT PAYMENT
            # ======================================

            calculated_rows = []

            for _, row in df.iterrows():

                monthly_salary = row.get(
                    "monthly_salary",
                    0
                )

                total_shifts = (
                    1
                    if is_present(
                        row.get("status")
                    )
                    else 0
                )

                salary_info = calculate_guard_salary(
                    monthly_salary=monthly_salary,
                    total_shifts=total_shifts,
                    year=selected_date.year,
                    month=selected_date.month
                )

                row_data = row.to_dict()

                row_data["total_days"] = (
                    salary_info["days_in_month"]
                )

                row_data["shift_rate"] = (
                    salary_info["shift_rate"]
                )

                row_data["actual_salary"] = (
                    salary_info["final_salary"]
                )

                calculated_rows.append(
                    row_data
                )

            df = pd.DataFrame(
                calculated_rows
            )

            # ======================================
            # SUMMARY
            # ======================================

            present_mask = df.get(
                "status",
                pd.Series(
                    "",
                    index=df.index
                )
            ).apply(
                is_present
            )

            total_shifts = int(
                present_mask.sum()
            )

            shift_1_count = int(
                (
                    present_mask
                    & (
                        df.get(
                            "shift_number",
                            pd.Series(
                                0,
                                index=df.index
                            )
                        ) == 1
                    )
                ).sum()
            )

            shift_2_count = int(
                (
                    present_mask
                    & (
                        df.get(
                            "shift_number",
                            pd.Series(
                                0,
                                index=df.index
                            )
                        ) == 2
                    )
                ).sum()
            )

            unique_guards = (
                df["guard_id"].nunique()
                if "guard_id" in df.columns
                else 0
            )

            total_actual_salary = (
                df["actual_salary"].sum()
                if "actual_salary" in df.columns
                else 0
            )

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:

                st.metric(
                    "Recorded Shifts",
                    total_shifts
                )

            with col2:

                st.metric(
                    "Shift 1",
                    shift_1_count
                )

            with col3:

                st.metric(
                    "Shift 2",
                    shift_2_count
                )

            with col4:

                st.metric(
                    "Unique Guards",
                    unique_guards
                )

            with col5:

                st.metric(
                    "Actual Salary",
                    format_currency(
                        total_actual_salary
                    )
                )

            st.divider()

            # ======================================
            # SEARCH
            # ======================================

            search_text = st.text_input(
                "🔍 Search by guard name or employee ID",
                key="guard_daily_search"
            )

            if search_text:

                search_value = (
                    search_text.lower()
                )

                guard_filter = (
                    df.get(
                        "guard_name",
                        pd.Series(
                            "",
                            index=df.index
                        )
                    )
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        search_value,
                        na=False
                    )
                )

                employee_filter = (
                    df.get(
                        "employee_id",
                        pd.Series(
                            "",
                            index=df.index
                        )
                    )
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        search_value,
                        na=False
                    )
                )

                df = df[
                    guard_filter | employee_filter
                ]

            # ======================================
            # TABLE
            # ONE ROW PER GUARD
            # Shift 1 / Shift 2 show the assigned site
            # ======================================

            display_df = build_guard_shift_table(
                df.to_dict(
                    orient="records"
                )
            )

            st.dataframe(
                display_df,
                width="stretch",
                hide_index=True,
                height=400
            )

    # ==============================================
    # MONTHLY GUARD RECORDS
    # ==============================================

    with monthly_tab:

        col1, col2 = st.columns(2)

        with col1:

            selected_month = st.selectbox(
                "Select Month",
                options=list(
                    range(1, 13)
                ),
                index=date.today().month - 1,
                format_func=lambda month: date(
                    2000,
                    month,
                    1
                ).strftime("%B"),
                key="guard_monthly_month"
            )

        with col2:

            selected_year = st.number_input(
                "Select Year",
                min_value=2020,
                max_value=2100,
                value=date.today().year,
                step=1,
                key="guard_monthly_year"
            )

        attendance = get_guard_monthly_attendance(
            int(selected_year),
            int(selected_month)
        )

        st.subheader(
            "📊 Monthly Guard Attendance"
        )

        if not attendance:

            st.info(
                "No guard records found."
            )

        else:

            df = pd.DataFrame(
                attendance
            )

            # ======================================
            # RECALCULATE MONTHLY SALARY
            #
            # Formula:
            # monthly_salary / days_in_month
            # × total_shifts
            # ======================================

            calculated_rows = []

            for _, row in df.iterrows():

                total_shifts = int(
                    row.get(
                        "total_shifts",
                        0
                    ) or 0
                )

                salary_info = calculate_guard_salary(
                    monthly_salary=row.get(
                        "monthly_salary",
                        0
                    ),
                    total_shifts=total_shifts,
                    year=int(selected_year),
                    month=int(selected_month)
                )

                row_data = row.to_dict()

                row_data["total_days"] = (
                    salary_info["days_in_month"]
                )

                row_data["shift_rate"] = (
                    salary_info["shift_rate"]
                )

                row_data["actual_salary"] = (
                    salary_info["final_salary"]
                )

                calculated_rows.append(
                    row_data
                )

            df = pd.DataFrame(
                calculated_rows
            )

            # ======================================
            # SUMMARY
            # ======================================

            total_guards = len(df)

            total_present_days = int(
                df["present_days"].sum()
                if "present_days" in df.columns
                else 0
            )

            total_shifts = int(
                df["total_shifts"].sum()
                if "total_shifts" in df.columns
                else 0
            )

            total_actual_salary = (
                df["actual_salary"].sum()
                if "actual_salary" in df.columns
                else 0
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Total Guards",
                    total_guards
                )

            with col2:

                st.metric(
                    "Present Days",
                    total_present_days
                )

            with col3:

                st.metric(
                    "Total Shifts",
                    total_shifts
                )

            with col4:

                st.metric(
                    "Actual Salary",
                    format_currency(
                        total_actual_salary
                    )
                )

            st.divider()

            # ======================================
            # SEARCH
            # ======================================

            search_text = st.text_input(
                "🔍 Search by guard name or employee ID",
                key="guard_monthly_search"
            )

            if search_text:

                search_value = (
                    search_text.lower()
                )

                guard_filter = (
                    df.get(
                        "guard_name",
                        pd.Series(
                            "",
                            index=df.index
                        )
                    )
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        search_value,
                        na=False
                    )
                )

                employee_filter = (
                    df.get(
                        "employee_id",
                        pd.Series(
                            "",
                            index=df.index
                        )
                    )
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        search_value,
                        na=False
                    )
                )

                df = df[
                    guard_filter | employee_filter
                ]

            # ======================================
            # TABLE
            # ONE ROW PER GUARD
            # ======================================

            table_data = []

            for _, row in df.iterrows():

                table_data.append({

                    "Employee ID": row.get(
                        "employee_id",
                        "-"
                    ),

                    "Guard Name": row.get(
                        "guard_name",
                        "Unknown Guard"
                    ),

                    "Shift 1": row.get(
                        "shift_1_count",
                        0
                    ),

                    "Shift 2": row.get(
                        "shift_2_count",
                        0
                    ),

                    "Total Shifts": row.get(
                        "total_shifts",
                        0
                    ),

                    "Total Days": row.get(
                        "total_days",
                        0
                    ),

                    "Monthly Salary": format_currency(
                        row.get(
                            "monthly_salary",
                            0
                        )
                    ),

                    "Shift Rate": format_currency(
                        row.get(
                            "shift_rate",
                            0
                        )
                    ),

                    "Actual Salary": format_currency(
                        row.get(
                            "actual_salary",
                            0
                        )
                    )
                })

            display_df = pd.DataFrame(
                table_data
            )

            st.dataframe(
                display_df,
                width="stretch",
                hide_index=True,
                height=400
            )

# ==================================================
# TAB 3 - SITE ATTENDANCE
# ==================================================

def show_site_attendance_tab():

    daily_tab, monthly_tab = st.tabs([
        "📅 Daily Records",
        "📊 Monthly Records"
    ])

    # ==============================================
    # DAILY SITE RECORDS
    # ==============================================

    with daily_tab:

        selected_date = st.date_input(
            "Select Date",
            value=date.today(),
            key="site_daily_attendance_date"
        )

        attendance = get_site_daily_attendance(
            selected_date
        )

        st.subheader(
            "🏢 Daily Site Attendance"
        )

        if not attendance:

            st.info(
                "No site attendance records found."
            )

        else:

            df = pd.DataFrame(
                attendance
            )

            # ======================================
            # DAILY SITE REVENUE
            #
            # One Present Shift =
            # monthly guard rate / days in month
            # ======================================

            calculated_rows = []

            for _, row in df.iterrows():

                total_shifts = (
                    1
                    if is_present(
                        row.get("status")
                    )
                    else 0
                )

                revenue_info = calculate_site_revenue(
                    monthly_rate=row.get(
                        "guard_rate",
                        0
                    ),
                    total_shifts=total_shifts,
                    year=selected_date.year,
                    month=selected_date.month
                )

                row_data = row.to_dict()

                row_data["total_days"] = (
                    revenue_info["days_in_month"]
                )

                row_data["shift_rate"] = (
                    revenue_info["shift_rate"]
                )

                row_data["actual_revenue"] = (
                    revenue_info["final_revenue"]
                )

                calculated_rows.append(
                    row_data
                )

            df = pd.DataFrame(
                calculated_rows
            )

            # ======================================
            # SUMMARY
            # ======================================

            total_sites = (
                df["site_id"].nunique()
                if "site_id" in df.columns
                else 0
            )

            present_mask = df.get(
                "status",
                pd.Series(
                    "",
                    index=df.index
                )
            ).apply(
                is_present
            )

            total_shifts = int(
                present_mask.sum()
            )

            total_actual_revenue = (
                df["actual_revenue"].sum()
                if "actual_revenue" in df.columns
                else 0
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Active Sites",
                    total_sites
                )

            with col2:

                st.metric(
                    "Recorded Shifts",
                    total_shifts
                )

            with col3:

                st.metric(
                    "Actual Revenue",
                    format_currency(
                        total_actual_revenue
                    )
                )

            st.divider()

            # ======================================
            # SEARCH
            # ======================================

            search_text = st.text_input(
                "🔍 Search by site name or site code",
                key="site_daily_search"
            )

            if search_text:

                search_value = (
                    search_text.lower()
                )

                site_name_filter = (
                    df.get(
                        "site_name",
                        pd.Series(
                            "",
                            index=df.index
                        )
                    )
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        search_value,
                        na=False
                    )
                )

                site_code_filter = (
                    df.get(
                        "site_code",
                        pd.Series(
                            "",
                            index=df.index
                        )
                    )
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        search_value,
                        na=False
                    )
                )

                df = df[
                    site_name_filter | site_code_filter
                ]

            # ======================================
            # TABLE
            # ONE ROW PER SITE
            # Shift 1 / Shift 2 = number of guards
            # ======================================

            display_df = build_site_shift_table(
                df.to_dict(
                    orient="records"
                )
            )

            st.dataframe(
                display_df,
                width="stretch",
                hide_index=True,
                height=400
            )

    # ==============================================
    # MONTHLY SITE RECORDS
    # ==============================================

    with monthly_tab:

        col1, col2 = st.columns(2)

        with col1:

            selected_month = st.selectbox(
                "Select Month",
                options=list(
                    range(1, 13)
                ),
                index=date.today().month - 1,
                format_func=lambda month: date(
                    2000,
                    month,
                    1
                ).strftime("%B"),
                key="site_monthly_month"
            )

        with col2:

            selected_year = st.number_input(
                "Select Year",
                min_value=2020,
                max_value=2100,
                value=date.today().year,
                step=1,
                key="site_monthly_year"
            )

        attendance = get_site_monthly_attendance(
            int(selected_year),
            int(selected_month)
        )

        st.subheader(
            "📊 Monthly Site Attendance"
        )

        if not attendance:

            st.info(
                "No site records found."
            )

        else:

            df = pd.DataFrame(
                attendance
            )

            # ======================================
            # RECALCULATE MONTHLY REVENUE
            #
            # monthly_rate / days_in_month
            # × total_shifts
            # ======================================

            calculated_rows = []

            for _, row in df.iterrows():

                total_shifts = int(
                    row.get(
                        "total_shifts",
                        0
                    ) or 0
                )

                revenue_info = calculate_site_revenue(
                    monthly_rate=row.get(
                        "guard_rate",
                        0
                    ),
                    total_shifts=total_shifts,
                    year=int(selected_year),
                    month=int(selected_month)
                )

                row_data = row.to_dict()

                row_data["total_days"] = (
                    revenue_info["days_in_month"]
                )

                row_data["shift_rate"] = (
                    revenue_info["shift_rate"]
                )

                row_data["actual_revenue"] = (
                    revenue_info["final_revenue"]
                )

                calculated_rows.append(
                    row_data
                )

            df = pd.DataFrame(
                calculated_rows
            )

            # ======================================
            # SUMMARY
            # ======================================

            total_sites = len(df)

            total_shifts = int(
                df["total_shifts"].sum()
                if "total_shifts" in df.columns
                else 0
            )

            total_actual_revenue = (
                df["actual_revenue"].sum()
                if "actual_revenue" in df.columns
                else 0
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Total Sites",
                    total_sites
                )

            with col2:

                st.metric(
                    "Completed Shifts",
                    total_shifts
                )

            with col3:

                st.metric(
                    "Actual Revenue",
                    format_currency(
                        total_actual_revenue
                    )
                )

            st.divider()

            # ======================================
            # SEARCH
            # ======================================

            search_text = st.text_input(
                "🔍 Search by site name or site code",
                key="site_monthly_search"
            )

            if search_text:

                search_value = (
                    search_text.lower()
                )

                site_name_filter = (
                    df.get(
                        "site_name",
                        pd.Series(
                            "",
                            index=df.index
                        )
                    )
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        search_value,
                        na=False
                    )
                )

                site_code_filter = (
                    df.get(
                        "site_code",
                        pd.Series(
                            "",
                            index=df.index
                        )
                    )
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        search_value,
                        na=False
                    )
                )

                df = df[
                    site_name_filter | site_code_filter
                ]

            # ======================================
            # TABLE
            # ONE ROW PER SITE
            # Shift 1 / Shift 2 = total guards worked
            # ======================================

            table_data = []

            for _, row in df.iterrows():

                site_code = row.get(
                    "site_code",
                    "-"
                )

                site_name = row.get(
                    "site_name",
                    "Unknown Site"
                )

                table_data.append({

                    "Site": (
                        f"{site_code} - {site_name}"
                    ),

                    "Shift 1": row.get(
                        "shift_1_count",
                        0
                    ),

                    "Shift 2": row.get(
                        "shift_2_count",
                        0
                    ),

                    "Total Shifts": row.get(
                        "total_shifts",
                        0
                    ),

                    "Total Days": row.get(
                        "total_days",
                        0
                    ),

                    "Monthly Rate": format_currency(
                        row.get(
                            "guard_rate",
                            0
                        )
                    ),

                    "Shift Rate": format_currency(
                        row.get(
                            "shift_rate",
                            0
                        )
                    ),

                    "Actual Revenue": format_currency(
                        row.get(
                            "actual_revenue",
                            0
                        )
                    )
                })

            display_df = pd.DataFrame(
                table_data
            )

            st.dataframe(
                display_df,
                width="stretch",
                hide_index=True,
                height=400
            )
