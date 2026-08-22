import streamlit as st
from datetime import date

from database.connection import SessionLocal

from database.models import User
from database.models import Guard
from database.models import Site

# Import these only if the models already exist
try:
    from database.models import Shift
except ImportError:
    Shift = None

try:
    from database.models import Incident
except ImportError:
    Incident = None

try:
    from database.models import Attendance
except ImportError:
    Attendance = None


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def get_dashboard_data():

    db = SessionLocal()

    try:

        # ------------------------------------------
        # GUARDS
        # ------------------------------------------

        total_guards = db.query(Guard).count()

        active_guards = (
            db.query(Guard)
            .filter(Guard.status == "Active")
            .count()
        )


        # ------------------------------------------
        # SITES
        # ------------------------------------------

        total_sites = db.query(Site).count()

        active_sites = (
            db.query(Site)
            .filter(Site.status == "Active")
            .count()
        )


        # ------------------------------------------
        # USERS
        # ------------------------------------------

        total_users = db.query(User).count()


        # ------------------------------------------
        # SHIFTS TODAY
        # ------------------------------------------

        shifts_today = 0

        if Shift:

            if hasattr(Shift, "date"):

                shifts_today = (
                    db.query(Shift)
                    .filter(
                        Shift.date == date.today()
                    )
                    .count()
                )

            elif hasattr(Shift, "shift_date"):

                shifts_today = (
                    db.query(Shift)
                    .filter(
                        Shift.shift_date == date.today()
                    )
                    .count()
                )


        # ------------------------------------------
        # OPEN INCIDENTS
        # ------------------------------------------

        open_incidents = 0

        if Incident and hasattr(Incident, "status"):

            open_incidents = (
                db.query(Incident)
                .filter(
                    Incident.status.in_([
                        "Open",
                        "In Progress"
                    ])
                )
                .count()
            )


        # ------------------------------------------
        # ATTENDANCE TODAY
        # ------------------------------------------

        attendance_today = 0

        if Attendance:

            if hasattr(Attendance, "check_in"):

                attendance_today = (
                    db.query(Attendance)
                    .filter(
                        Attendance.check_in >= date.today()
                    )
                    .count()
                )


        return {

            "total_guards": total_guards,
            "active_guards": active_guards,

            "total_sites": total_sites,
            "active_sites": active_sites,

            "total_users": total_users,

            "shifts_today": shifts_today,

            "open_incidents": open_incidents,

            "attendance_today": attendance_today,
        }


    finally:

        db.close()


# ==================================================
# DASHBOARD
# ==================================================

def show_dashboard():

    # ==============================================
    # LOAD DATA
    # ==============================================

    data = get_dashboard_data()


    # ==============================================
    # HEADER
    # ==============================================

    user = st.session_state.get(
        "user",
        {}
    )

    username = user.get(
        "username",
        "User"
    )

    st.markdown(
        f"# Welcome back, {username} 👋"
    )

    st.caption(
        "Here's what's happening with your security operations today."
    )

    st.divider()


    # ==============================================
    # PRIMARY STATISTICS
    # ==============================================

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            label="👮 Total Guards",
            value=data["total_guards"],
            delta=f'{data["active_guards"]} Active'
        )


    with col2:

        st.metric(
            label="🏢 Total Sites",
            value=data["total_sites"],
            delta=f'{data["active_sites"]} Active'
        )


    with col3:

        st.metric(
            label="📅 Shifts Today",
            value=data["shifts_today"]
        )


    with col4:

        st.metric(
            label="🚨 Open Incidents",
            value=data["open_incidents"]
        )


    st.markdown("<br>", unsafe_allow_html=True)


    # ==============================================
    # SECONDARY STATISTICS
    # ==============================================

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            label="📍 Check-ins Today",
            value=data["attendance_today"]
        )


    with col2:

        st.metric(
            label="👥 System Users",
            value=data["total_users"]
        )


    with col3:

        inactive_guards = (
            data["total_guards"]
            - data["active_guards"]
        )

        st.metric(
            label="⚠️ Inactive Guards",
            value=inactive_guards
        )


    st.divider()


    # ==============================================
    # OPERATIONAL OVERVIEW
    # ==============================================

    st.subheader("📊 Operational Overview")

    col1, col2 = st.columns(2)


    with col1:

        st.info(
            f"""
            **Guard Status**

            Total Guards: {data["total_guards"]}

            Active Guards: {data["active_guards"]}

            Inactive Guards:
            {data["total_guards"] - data["active_guards"]}
            """
        )


    with col2:

        st.info(
            f"""
            **Site Status**

            Total Sites: {data["total_sites"]}

            Active Sites: {data["active_sites"]}

            Inactive Sites:
            {data["total_sites"] - data["active_sites"]}
            """
        )


    st.divider()


    # ==============================================
    # QUICK ACTIONS
    # ==============================================

    st.subheader("⚡ Quick Actions")

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        if st.button(
            "➕ Add Guard",
            use_container_width=True
        ):

            st.session_state["selected_page"] = "Guards"

            st.rerun()


    with col2:

        if st.button(
            "🏢 Add Site",
            use_container_width=True
        ):

            st.session_state["selected_page"] = "Sites"

            st.rerun()


    with col3:

        if st.button(
            "📅 Manage Shifts",
            use_container_width=True
        ):

            st.session_state["selected_page"] = "Shifts"

            st.rerun()


    with col4:

        if st.button(
            "🚨 Report Incident",
            use_container_width=True
        ):

            st.session_state["selected_page"] = "Incidents"

            st.rerun()