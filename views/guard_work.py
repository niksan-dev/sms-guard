import streamlit as st
import pandas as pd
from datetime import date

from services.guard_daily_work_service import (
    create_guard_daily_work,
    get_daily_work_records,
    delete_daily_work,
    get_daily_work_summary,
    get_guard_daily_attendance,
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

    st.subheader("Record Guard Shift")

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

    shift_number = st.radio(
        "Shift",
        options=[1, 2],
        horizontal=True,
        format_func=lambda x: f"Shift {x}"
    )

    status = st.selectbox(
        "Status",
        options=[
            "Present",
            "Absent"
        ],
        index=0
    )

    if st.button(
        "💾 Record Shift",
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
# SHOW DAILY WORK RECORDS
# ==================================================

def show_daily_work_records(selected_date):

    st.subheader("Today's Recorded Shifts")

    records = get_daily_work_records(
        selected_date
    )

    if not records:

        st.info(
            "No shifts recorded for this date."
        )

        return

    summary = get_daily_work_summary(
        selected_date
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Shifts",
            summary["total_shifts"]
        )

    with col2:

        st.metric(
            "Shift 1",
            summary["shift_1_count"]
        )

    with col3:

        st.metric(
            "Shift 2",
            summary["shift_2_count"]
        )

    with col4:

        st.metric(
            "Unique Guards",
            summary["unique_guards"]
        )

    st.markdown("<br>", unsafe_allow_html=True)

    for record in records:

        guard_name = (
            record.guard.name
            if record.guard
            else "Unknown Guard"
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

        col1, col2, col3, col4, col5 = st.columns(
            [3, 3, 1.5, 1.5, 1]
        )

        with col1:

            st.write(
                f"**👮 {guard_name}**"
            )

        with col2:

            st.write(
                f"🏢 {site_code} - {site_name}"
            )

        with col3:

            st.write(
                f"Shift {record.shift_number}"
            )

        with col4:

            if record.status == "Present":

                st.success(
                    record.status
                )

            else:

                st.warning(
                    record.status
                )

        with col5:

            if st.button(
                "🗑️",
                key=f"delete_work_{record.id}",
                help="Delete work record"
            ):

                success, message = delete_daily_work(
                    record.id
                )

                if success:

                    st.success(message)

                    st.rerun()

                else:

                    st.error(message)

        st.divider()


# ==================================================
# TAB 2 - GUARD ATTENDANCE
# ==================================================

def show_guard_attendance_tab():

    selected_date = st.date_input(
        "Select Date",
        value=date.today(),
        key="guard_attendance_date"
    )

    attendance = get_guard_daily_attendance(
        selected_date
    )

    if not attendance:

        st.info(
            "No guard attendance records found."
        )

        return

    df = pd.DataFrame(attendance)

    display_columns = [
        "guard_name",
        "site_name",
        "shift_number",
        "status"
    ]

    df = df[display_columns]

    df.columns = [
        "Guard",
        "Site",
        "Shift",
        "Status"
    ]

    df["Shift"] = (
        "Shift "
        + df["Shift"].astype(str)
    )

    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )

    total_guards = len(
        attendance
    )

    shift_1 = len([
        item
        for item in attendance
        if item["shift_number"] == 1
    ])

    shift_2 = len([
        item
        for item in attendance
        if item["shift_number"] == 2
    ])

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Recorded Shifts",
            total_guards
        )

    with col2:

        st.metric(
            "Shift 1 Attendance",
            shift_1
        )

    with col3:

        st.metric(
            "Shift 2 Attendance",
            shift_2
        )


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

    if not attendance:

        st.info(
            "No site attendance records found."
        )

        return

    df = pd.DataFrame(attendance)

    display_columns = [
        "site_name",
        "guard_name",
        "shift_number",
        "status"
    ]

    df = df[display_columns]

    df.columns = [
        "Site",
        "Guard",
        "Shift",
        "Status"
    ]

    df["Shift"] = (
        "Shift "
        + df["Shift"].astype(str)
    )

    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )

    total_sites = len(
        set(
            item["site_id"]
            for item in attendance
        )
    )

    total_shifts = len(
        attendance
    )

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