import streamlit as st
import pandas as pd
from datetime import date
import calendar


# ==================================================
# SERVICES - GUARD WORK LOG
# ==================================================


# ==================================================
# SERVICES - DAILY WORK / ATTENDANCE
# ==================================================

from services.guard_work_log_service import (
    create_guard_work_log,
    get_work_logs_by_date,
    delete_guard_work_log,
    get_daily_work_summary,
    get_guard_daily_attendance,
    get_site_daily_attendance
)


# ==================================================
# OTHER SERVICES
# ==================================================

from services.site_service import get_all_sites
from services.guard_service import get_all_guards


# ==================================================
# HELPERS
# ==================================================

def get_active_sites():

    sites = get_all_sites()

    return [
        site
        for site in sites
        if (site.status or "").lower() == "active"
    ]


def get_active_guards():

    guards = get_all_guards()

    return [
        guard
        for guard in guards
        if (guard.status or "").lower() == "active"
    ]


def format_currency(amount):

    return f"₹ {float(amount or 0):,.2f}"


def get_days_in_month(target_date):
    """
    Returns the actual number of days in the month.

    January  -> 31
    February -> 28 / 29
    April    -> 30
    """

    return calendar.monthrange(
        target_date.year,
        target_date.month
    )[1]


# ==================================================
# MAIN PAGE
# ==================================================

def show_guard_work():

    # ==================================================
    # PAGE HEADER
    # ==================================================

    st.title("👷 Guard Work Management")

    st.caption(
        "Record guard shifts and monitor daily guard and site attendance."
    )

    st.divider()


    # ==================================================
    # TABS
    # ==================================================

    (
        tab_record,
        tab_guard_attendance,
        tab_site_attendance
    ) = st.tabs([
        "📝 Record Work",
        "👮 Guard Attendance",
        "🏢 Site Attendance"
    ])


    # ==================================================
    # TAB 1 - RECORD WORK
    # ==================================================

    with tab_record:

        show_record_work_tab()


    # ==================================================
    # TAB 2 - GUARD ATTENDANCE
    # ==================================================

    with tab_guard_attendance:

        show_guard_attendance_tab()


    # ==================================================
    # TAB 3 - SITE ATTENDANCE
    # ==================================================

    with tab_site_attendance:

        show_site_attendance_tab()


# ==================================================
# TAB 1 - RECORD GUARD WORK
# ==================================================

def show_record_work_tab():

    st.subheader("📝 Record Guard Shift")

    st.caption(
        "Record Shift 1 or Shift 2 for a guard."
    )


    # ==================================================
    # LOAD ACTIVE DATA
    # ==================================================

    sites = get_active_sites()
    guards = get_active_guards()


    if not sites:

        st.warning(
            "No active sites available."
        )

        return


    if not guards:

        st.warning(
            "No active guards available."
        )

        return


    # ==================================================
    # RECORD FORM
    # ==================================================

    with st.form("record_guard_work_form"):

        col1, col2 = st.columns(2)


        # ----------------------------------------------
        # WORK DATE
        # ----------------------------------------------

        with col1:

            work_date = st.date_input(
                "📅 Work Date",
                value=date.today()
            )


        # ----------------------------------------------
        # SITE
        # ----------------------------------------------

        with col2:

            site_options = {
                f"{site.site_code} - {site.name}": site
                for site in sites
            }

            selected_site_label = st.selectbox(
                "🏢 Select Site",
                options=list(site_options.keys())
            )

            selected_site = site_options[
                selected_site_label
            ]


        # ----------------------------------------------
        # GUARD
        # ----------------------------------------------

        guard_options = {
            f"{guard.employee_id} - {guard.name}": guard
            for guard in guards
        }

        selected_guard_label = st.selectbox(
            "👮 Select Guard",
            options=list(guard_options.keys())
        )

        selected_guard = guard_options[
            selected_guard_label
        ]


        # ----------------------------------------------
        # SHIFT
        # ----------------------------------------------

        shift_number = st.selectbox(
            "🕐 Select Shift",
            options=[1, 2],
            format_func=lambda x: f"Shift {x}"
        )


        # ----------------------------------------------
        # FINANCIAL PREVIEW
        # ----------------------------------------------

        days_in_month = get_days_in_month(
            work_date
        )

        monthly_salary = float(
            selected_guard.monthly_salary or 0
        )

        monthly_rate = float(
            selected_site.guard_rate or 0
        )

        daily_salary_preview = (
            monthly_salary / days_in_month
        )

        daily_revenue_preview = (
            monthly_rate / days_in_month
        )


        st.divider()

        st.markdown(
            "#### 💰 Shift Financial Preview"
        )

        col1, col2, col3, col4 = st.columns(4)


        with col1:

            st.metric(
                "Guard Monthly Salary",
                format_currency(monthly_salary)
            )


        with col2:

            st.metric(
                "Site Guard Rate",
                format_currency(monthly_rate)
            )


        with col3:

            st.metric(
                "Salary Per Shift",
                format_currency(
                    daily_salary_preview
                )
            )


        with col4:

            st.metric(
                "Revenue Per Shift",
                format_currency(
                    daily_revenue_preview
                )
            )


        st.divider()


        # ----------------------------------------------
        # SUBMIT
        # ----------------------------------------------

        submitted = st.form_submit_button(
            "➕ Record Shift",
            type="primary",
            width="stretch"
        )


    # ==================================================
    # SAVE SHIFT
    # ==================================================

    if submitted:

        try:

            success, message = create_guard_work_log(

                work_date=work_date,

                guard_id=selected_guard.id,

                site_id=selected_site.id,

                shift_number=shift_number,

                status="Present"
            )


            if not success:

                st.error(message)

                return


            # ------------------------------------------
            # SAVE / UPDATE DAILY FINANCIAL RECORD
            # ------------------------------------------

            save_guard_daily_work(

                work_date=work_date,

                guard_id=selected_guard.id,

                site_id=selected_site.id
            )


            st.success(
                message
            )

            st.rerun()


        except Exception as e:

            st.error(
                f"Unable to record shift: {str(e)}"
            )


    # ==================================================
    # DAILY SUMMARY
    # ==================================================

    st.divider()

    st.subheader("📊 Daily Work Summary")


    summary_date = st.date_input(
        "Select Date for Summary",
        value=date.today(),
        key="work_summary_date"
    )


    try:

        summary = get_daily_work_summary(
            summary_date
        )

        if summary:

            col1, col2, col3 = st.columns(3)


            with col1:

                st.metric(
                    "👮 Total Guards",
                    summary.get(
                        "total_guards",
                        0
                    )
                )


            with col2:

                st.metric(
                    "🕐 Total Shifts",
                    summary.get(
                        "total_shifts",
                        0
                    )
                )


            with col3:

                st.metric(
                    "🏢 Sites Covered",
                    summary.get(
                        "total_sites",
                        0
                    )
                )

    except Exception:

        pass


    # ==================================================
    # RECORDED SHIFT LOGS
    # ==================================================

    st.divider()

    st.subheader("📋 Recorded Shifts")


    try:

        logs = get_work_logs_by_date(
            summary_date
        )

    except Exception as e:

        st.error(
            f"Unable to load work logs: {str(e)}"
        )

        return


    if not logs:

        st.info(
            "No shifts recorded for this date."
        )

        return


    display_data = []


    for log in logs:

        guard_name = "Unknown"
        employee_id = ""
        site_name = "Unknown"

        if hasattr(log, "guard") and log.guard:

            guard_name = (
                log.guard.name or "Unknown"
            )

            employee_id = (
                log.guard.employee_id or ""
            )


        if hasattr(log, "site") and log.site:

            site_name = (
                f"{log.site.site_code} - "
                f"{log.site.name}"
            )


        display_data.append({

            "ID": log.id,

            "Employee ID": employee_id,

            "Guard": guard_name,

            "Site": site_name,

            "Shift":
                f"Shift {log.shift_number}",

            "Status":
                log.status or "Present"
        })


    df = pd.DataFrame(
        display_data
    )


    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )


    # ==================================================
    # DELETE SHIFT
    # ==================================================

    st.divider()

    with st.expander(
        "🗑️ Delete Recorded Shift"
    ):

        delete_options = {
            f"{row['Guard']} | "
            f"{row['Site']} | "
            f"{row['Shift']}": row["ID"]

            for _, row in df.iterrows()
        }


        selected_delete_label = st.selectbox(
            "Select Shift Record",
            options=list(
                delete_options.keys()
            ),
            key="delete_work_log_selector"
        )


        if st.button(
            "🗑️ Delete Shift",
            type="primary",
            width="stretch",
            key="delete_guard_shift_button"
        ):

            try:

                log_id = delete_options[
                    selected_delete_label
                ]

                success, message = (
                    delete_guard_work_log(
                        log_id
                    )
                )


                if success:

                    st.success(message)

                    st.rerun()

                else:

                    st.error(message)


            except Exception as e:

                st.error(str(e))


# ==================================================
# TAB 2 - GUARD DAILY ATTENDANCE
# ==================================================

def show_guard_attendance_tab():

    st.subheader("👮 Guard Daily Attendance")

    st.caption(
        "View Shift 1 and Shift 2 attendance for every guard."
    )


    # ==================================================
    # FILTERS
    # ==================================================

    col1, col2 = st.columns(2)


    with col1:

        selected_date = st.date_input(
            "📅 Select Date",
            value=date.today(),
            key="guard_attendance_date"
        )


    with col2:

        sites = get_active_sites()

        site_options = {
            "All Sites": None
        }

        for site in sites:

            site_options[
                f"{site.site_code} - {site.name}"
            ] = site.id


        selected_site_label = st.selectbox(
            "🏢 Filter by Site",
            options=list(
                site_options.keys()
            ),
            key="guard_attendance_site"
        )


        selected_site_id = site_options[
            selected_site_label
        ]


    st.divider()


    # ==================================================
    # LOAD ATTENDANCE
    # ==================================================

    try:

        attendance_data = (
            get_guard_daily_attendance(
                work_date=selected_date,
                site_id=selected_site_id
            )
        )

    except Exception as e:

        st.error(
            f"Unable to load attendance: {str(e)}"
        )

        return


    # ==================================================
    # SUMMARY
    # ==================================================

    total_guards = len(
        attendance_data
    )

    present_guards = sum(
        1
        for record in attendance_data
        if record.get("status") == "Present"
    )

    absent_guards = (
        total_guards - present_guards
    )

    shift_1_present = sum(
        1
        for record in attendance_data
        if record.get("shift_1") == "Present"
    )

    shift_2_present = sum(
        1
        for record in attendance_data
        if record.get("shift_2") == "Present"
    )


    # ==================================================
    # METRICS
    # ==================================================

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "👮 Total Guards",
            total_guards
        )


    with col2:

        st.metric(
            "✅ Present",
            present_guards
        )


    with col3:

        st.metric(
            "☀️ Shift 1",
            shift_1_present
        )


    with col4:

        st.metric(
            "🌙 Shift 2",
            shift_2_present
        )


    st.caption(
        f"❌ Absent Guards: {absent_guards}"
    )


    st.divider()


    # ==================================================
    # SEARCH
    # ==================================================

    search = st.text_input(
        "🔍 Search Guard",
        placeholder=(
            "Search by guard name or employee ID..."
        ),
        key="guard_attendance_search"
    )


    # ==================================================
    # TABLE DATA
    # ==================================================

    display_data = []


    for record in attendance_data:

        display_data.append({

            "Employee ID":
                record.get(
                    "employee_id",
                    ""
                ),

            "Guard Name":
                record.get(
                    "guard_name",
                    ""
                ),

            "Site":
                record.get(
                    "site",
                    "-"
                ),

            "Shift 1":

                "✅ Present"

                if record.get(
                    "shift_1"
                ) == "Present"

                else "❌ Absent",

            "Shift 2":

                "✅ Present"

                if record.get(
                    "shift_2"
                ) == "Present"

                else "❌ Absent",

            "Total Shifts":
                record.get(
                    "total_shifts",
                    0
                ),

            "Status":

                "🟢 Present"

                if record.get(
                    "status"
                ) == "Present"

                else "🔴 Absent"
        })


    df = pd.DataFrame(
        display_data
    )


    # ==================================================
    # SEARCH FILTER
    # ==================================================

    if search and not df.empty:

        search = search.strip().lower()


        mask = (

            df["Employee ID"]
            .astype(str)
            .str.lower()
            .str.contains(
                search,
                na=False
            )

            |

            df["Guard Name"]
            .astype(str)
            .str.lower()
            .str.contains(
                search,
                na=False
            )

        )


        df = df[mask]


    # ==================================================
    # DISPLAY
    # ==================================================

    if df.empty:

        st.info(
            "No attendance data found."
        )

    else:

        st.dataframe(
            df,
            width="stretch",
            hide_index=True,
            height=500
        )


    st.caption(
        "Showing attendance for "
        f"{selected_date.strftime('%d %B %Y')}"
    )


# ==================================================
# TAB 3 - SITE DAILY ATTENDANCE
# ==================================================

def show_site_attendance_tab():

    st.subheader("🏢 Site Daily Attendance")

    st.caption(
        "Monitor guard coverage for Shift 1 and Shift 2."
    )


    # ==================================================
    # DATE
    # ==================================================

    selected_date = st.date_input(
        "📅 Select Date",
        value=date.today(),
        key="site_attendance_date"
    )


    st.divider()


    # ==================================================
    # LOAD DATA
    # ==================================================

    try:

        attendance_data = (
            get_site_daily_attendance(
                work_date=selected_date
            )
        )

    except Exception as e:

        st.error(
            f"Unable to load site attendance: {str(e)}"
        )

        return


    # ==================================================
    # SUMMARY
    # ==================================================

    total_sites = len(
        attendance_data
    )

    total_required = sum(
        int(
            record.get(
                "required_guards",
                0
            ) or 0
        )

        for record in attendance_data
    )

    total_shift_1 = sum(
        int(
            record.get(
                "shift_1_present",
                0
            ) or 0
        )

        for record in attendance_data
    )

    total_shift_2 = sum(
        int(
            record.get(
                "shift_2_present",
                0
            ) or 0
        )

        for record in attendance_data
    )


    # ==================================================
    # METRICS
    # ==================================================

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "🏢 Total Sites",
            total_sites
        )


    with col2:

        st.metric(
            "👮 Guards Required",
            total_required
        )


    with col3:

        st.metric(
            "☀️ Shift 1 Coverage",
            f"{total_shift_1} / {total_required}"
        )


    with col4:

        st.metric(
            "🌙 Shift 2 Coverage",
            f"{total_shift_2} / {total_required}"
        )


    st.divider()


    # ==================================================
    # SEARCH
    # ==================================================

    search = st.text_input(
        "🔍 Search Site",
        placeholder=(
            "Search by site code or site name..."
        ),
        key="site_attendance_search"
    )


    # ==================================================
    # PREPARE DATA
    # ==================================================

    display_data = []


    for record in attendance_data:

        required = int(
            record.get(
                "required_guards",
                0
            ) or 0
        )

        shift_1 = int(
            record.get(
                "shift_1_present",
                0
            ) or 0
        )

        shift_2 = int(
            record.get(
                "shift_2_present",
                0
            ) or 0
        )

        total_shifts = (
            shift_1 + shift_2
        )


        # ----------------------------------------------
        # SHIFT 1 STATUS
        # ----------------------------------------------

        if required == 0:

            shift_1_display = (
                f"{shift_1} / -"
            )

        elif shift_1 >= required:

            shift_1_display = (
                f"✅ {shift_1} / {required}"
            )

        else:

            shift_1_display = (
                f"⚠️ {shift_1} / {required}"
            )


        # ----------------------------------------------
        # SHIFT 2 STATUS
        # ----------------------------------------------

        if required == 0:

            shift_2_display = (
                f"{shift_2} / -"
            )

        elif shift_2 >= required:

            shift_2_display = (
                f"✅ {shift_2} / {required}"
            )

        else:

            shift_2_display = (
                f"⚠️ {shift_2} / {required}"
            )


        # ----------------------------------------------
        # OVERALL COVERAGE
        # ----------------------------------------------

        expected_total = (
            required * 2
        )


        if expected_total == 0:

            coverage = (
                "⚪ No Requirement"
            )

        elif total_shifts >= expected_total:

            coverage = (
                "🟢 Fully Covered"
            )

        elif total_shifts > 0:

            coverage = (
                "🟠 Partially Covered"
            )

        else:

            coverage = (
                "🔴 No Coverage"
            )


        display_data.append({

            "Site Code":
                record.get(
                    "site_code",
                    ""
                ),

            "Site Name":
                record.get(
                    "site_name",
                    ""
                ),

            "Guards Required":
                required,

            "Shift 1":
                shift_1_display,

            "Shift 2":
                shift_2_display,

            "Total Shifts":
                total_shifts,

            "Coverage":
                coverage
        })


    df = pd.DataFrame(
        display_data
    )


    # ==================================================
    # SEARCH FILTER
    # ==================================================

    if search and not df.empty:

        search = search.strip().lower()


        mask = (

            df["Site Code"]
            .astype(str)
            .str.lower()
            .str.contains(
                search,
                na=False
            )

            |

            df["Site Name"]
            .astype(str)
            .str.lower()
            .str.contains(
                search,
                na=False
            )

        )


        df = df[mask]


    # ==================================================
    # DISPLAY TABLE
    # ==================================================

    if df.empty:

        st.info(
            "No site attendance data found."
        )

    else:

        st.dataframe(
            df,
            width="stretch",
            hide_index=True,
            height=500
        )


    st.caption(
        "Showing site attendance for "
        f"{selected_date.strftime('%d %B %Y')}"
    )