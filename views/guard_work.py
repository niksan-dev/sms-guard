import streamlit as st
import pandas as pd
from datetime import date

from services.guard_daily_work_service import (
    create_guard_daily_work,
    get_daily_work_records,
    delete_daily_work,
    get_daily_work_summary,
    get_guard_daily_attendance,
    get_guard_monthly_attendance,
    get_site_daily_attendance,
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

    return f"Shift {shift_number}"


# ==================================================
# MAIN PAGE
# ==================================================

def show_guard_work():

    st.title("👮 Guard Work Management")

    st.caption(
        "Record daily guard shifts and monitor guard and site attendance."
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
        st.warning("No active guards available.")
        return

    if not sites:
        st.warning("No active sites available.")
        return

    st.subheader("📝 Record Guard Shift")

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

    show_daily_work_records(selected_date)


# ==================================================
# RECORDED SHIFTS
# ==================================================

# ==================================================
# RECORDED SHIFTS - TABULAR VIEW
# ==================================================

# ==================================================
# RECORDED SHIFTS - TABLE VIEW
# ==================================================

def show_daily_work_records(selected_date):

    records = get_daily_work_records(
        selected_date
    )

    st.subheader("📋 Recorded Shifts")

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
            summary.get("total_shifts", 0)
        )

    with col2:
        st.metric(
            "Shift 1",
            summary.get("shift_1_count", 0)
        )

    with col3:
        st.metric(
            "Shift 2",
            summary.get("shift_2_count", 0)
        )

    with col4:
        st.metric(
            "Unique Guards",
            summary.get("unique_guards", 0)
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ==============================================
    # BUILD TABLE DATA
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
            else ""
        )

        table_data.append({
            "ID": record.id,
            "Employee ID": employee_id,
            "Guard": guard_name,
            "Site": f"{site_code} - {site_name}",
            "Shift": f"Shift {record.shift_number}",
            "Status": record.status,
        })

    # ==============================================
    # DISPLAY PROPER TABLE
    # ==============================================

    df = pd.DataFrame(table_data)

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
                width="medium"
            ),

            "Status": st.column_config.TextColumn(
                "Status",
                width="medium"
            ),
        }
    )

    # ==================================================
    # DELETE RECORDED SHIFT
    # ==================================================

    st.markdown("### Delete a recorded shift")

    if records:

        delete_options = {
            f"{record.id} - "
            f"{record.guard.name if record.guard else 'Unknown Guard'} - "
            f"Shift {record.shift_number}": record.id
            for record in records
        }

        col1, col2 = st.columns(
            [1, 1],
            vertical_alignment="bottom"
        )

        with col1:

            selected_delete_label = st.selectbox(
                "Select shift to delete",
                options=list(delete_options.keys()),
                key="delete_shift_select"
            )

        with col2:

            # Empty label keeps button aligned with selectbox
            st.markdown(
                "<div style='height: 28px;'></div>",
                unsafe_allow_html=True
            )

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
# TAB 3 - SITE ATTENDANCE
# ==================================================

def show_site_attendance_tab():

    selected_date = st.date_input(
        "Select Date",
        value=date.today(),
        key="site_attendance_date"
    )

    attendance = get_site_daily_attendance(
        selected_date
    )

    st.subheader("🏢 Site Attendance")

    if not attendance:

        st.info(
            "No site attendance records found."
        )

        return

    df = pd.DataFrame(attendance)


    total_sites = len(
        set(
            item.get("site_id")
            for item in attendance
            if item.get("site_id") is not None
        )
    )

    total_shifts = len(attendance)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

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

    required_columns = [
        "site_name",
        "guard_name",
        "shift_number",
        "status"
    ]

    df = df[
        [
            column
            for column in required_columns
            if column in df.columns
        ]
    ]

    if "shift_number" in df.columns:

        df["shift_number"] = (
            "Shift "
            + df["shift_number"].astype(str)
        )

    df.columns = [
        "Site",
        "Guard",
        "Shift",
        "Status"
    ]

    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )

    

def show_guard_attendance_tab():

    daily_tab, monthly_tab = st.tabs([
        "📅 Daily Records",
        "📊 Monthly Records"
    ])

    # ==========================================
    # DAILY RECORDS
    # ==========================================

    with daily_tab:

        selected_date = st.date_input(
            "Select Date",
            value=date.today(),
            key="guard_daily_attendance_date"
        )

        attendance = get_guard_daily_attendance(selected_date)

        if not attendance:

            st.info(
                "No guard attendance records found for this date."
            )

        else:

            df = pd.DataFrame(attendance)


            # ----------------------------------
            # DAILY SUMMARY
            # ----------------------------------

            total_shifts = len(df)

            shift_1_count = len(
                df[
                    df["shift_number"] == 1
                ]
            )

            shift_2_count = len(
                df[
                    df["shift_number"] == 2
                ]
            )

            unique_guards = df[
                "guard_id"
            ].nunique()

            st.markdown("<br>", unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)

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

            # ----------------------------------
            # SEARCH
            # ----------------------------------

            st.divider()

            st.caption("🔍 Search Guard")

            search_text = st.text_input(
                "Search by guard name or employee ID...",
                label_visibility="collapsed",
                key="guard_daily_search"
            )

            if search_text:

                search_value = search_text.lower()

                df = df[
                    df["guard_name"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        search_value,
                        na=False
                    )
                    |
                    df["employee_id"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        search_value,
                        na=False
                    )
                ]

            # ----------------------------------
            # DISPLAY TABLE
            # ----------------------------------

            display_df = df[[
                "employee_id",
                "guard_name",
                "site_code",
                "site_name",
                "shift_number",
                "status"
            ]].copy()

            display_df["Site"] = (
                display_df["site_code"].astype(str)
                + " - "
                + display_df["site_name"].astype(str)
            )

            display_df["Shift"] = (
                "Shift "
                + display_df["shift_number"].astype(str)
            )

            display_df = display_df[[
                "employee_id",
                "guard_name",
                "Site",
                "Shift",
                "status"
            ]]

            display_df.columns = [
                "Employee ID",
                "Guard Name",
                "Site",
                "Shift",
                "Status"
            ]

            st.dataframe(
                display_df,
                width="stretch",
                hide_index=True,
                height=400
            )

            

    # ==========================================
    # MONTHLY RECORDS
    # ==========================================

    with monthly_tab:

        col1, col2 = st.columns(2)

        with col1:

            selected_month = st.selectbox(
                "Select Month",
                options=list(range(1, 13)),
                index=date.today().month - 1,
                format_func=lambda month:
                    date(
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

        if not attendance:

            st.info(
                "No guard records found."
            )

        else:

            df = pd.DataFrame(attendance)


            # ----------------------------------
            # MONTHLY SUMMARY
            # ----------------------------------

            total_guards = len(df)

            total_present_days = int(
                df["present_days"].sum()
            )

            total_shift_1 = int(
                df["shift_1_count"].sum()
            )

            total_shift_2 = int(
                df["shift_2_count"].sum()
            )

            total_shifts = int(
                df["total_shifts"].sum()
            )

            st.markdown("<br>", unsafe_allow_html=True)

            col1, col2, col3, col4, col5 = st.columns(5)

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
                    "Shift 1",
                    total_shift_1
                )

            with col4:

                st.metric(
                    "Shift 2",
                    total_shift_2
                )

            with col5:

                st.metric(
                    "Total Shifts",
                    total_shifts
                )

            # ----------------------------------
            # SEARCH
            # ----------------------------------

            st.divider()

            st.caption("🔍 Search Guard")

            search_text = st.text_input(
                "Search by guard name or employee ID...",
                label_visibility="collapsed",
                key="guard_monthly_search"
            )

            if search_text:

                search_value = search_text.lower()

                df = df[
                    df["guard_name"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        search_value,
                        na=False
                    )
                    |
                    df["employee_id"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        search_value,
                        na=False
                    )
                ]

            # ----------------------------------
            # MONTHLY TABLE
            # ----------------------------------

            display_df = df[[
                "employee_id",
                "guard_name",
                "present_days",
                "shift_1_count",
                "shift_2_count",
                "total_shifts"
            ]].copy()

            display_df.columns = [
                "Employee ID",
                "Guard Name",
                "Present Days",
                "Shift 1",
                "Shift 2",
                "Total Shifts"
            ]

            st.dataframe(
                display_df,
                width="stretch",
                hide_index=True,
                height=400
            )

            