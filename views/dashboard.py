import streamlit as st
from datetime import date

import plotly.express as px
import pandas as pd

from sqlalchemy import or_

from database.connection import SessionLocal
from database.models import User
from database.models import Guard
from database.models import Site


# ==================================================
# OPTIONAL MODELS
# ==================================================

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
# DASHBOARD CARD
# ==================================================

def dashboard_card(
    title,
    value,
    icon,
    icon_class,
    footer,
    footer_class=""
):

    st.html(
        f"""
<div class="dashboard-card">

    <div class="dashboard-card-top">

        <div class="dashboard-card-title">
            {title}
        </div>

        <div class="dashboard-card-icon {icon_class}">
            {icon}
        </div>

    </div>

    <div class="dashboard-card-value">
        {value}
    </div>

    <div class="dashboard-card-footer {footer_class}">
        {footer}
    </div>

</div>
"""
    )


# ==================================================
# GET DASHBOARD DATA
# ==================================================

def get_dashboard_data():

    db = SessionLocal()

    try:

        # ==========================================
        # GUARDS
        # ==========================================

        total_guards = db.query(Guard).count()

        active_guards = (
            db.query(Guard)
            .filter(Guard.status == "Active")
            .count()
        )


        # ==========================================
        # SITES
        # ==========================================

        total_sites = db.query(Site).count()

        active_sites = (
            db.query(Site)
            .filter(Site.status == "Active")
            .count()
        )


        # ==========================================
        # USERS
        # ==========================================

        total_users = db.query(User).count()


        # ==========================================
        # SHIFTS TODAY
        # ==========================================

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


        # ==========================================
        # OPEN INCIDENTS
        # ==========================================

        open_incidents = 0

        if Incident and hasattr(Incident, "status"):

            open_incidents = (
                db.query(Incident)
                .filter(
                    Incident.status.in_(
                        [
                            "Open",
                            "In Progress"
                        ]
                    )
                )
                .count()
            )


        # ==========================================
        # ATTENDANCE TODAY
        # ==========================================

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


        # ==========================================
        # RETURN DATA
        # ==========================================

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
# GET ANALYTICS CHART DATA
# ==================================================

def get_status_chart_data():

    db = SessionLocal()

    try:

        # ==========================================
        # GUARD STATUS
        # ==========================================

        active_guards = (
            db.query(Guard)
            .filter(Guard.status == "Active")
            .count()
        )


        inactive_guards = (
            db.query(Guard)
            .filter(
                or_(
                    Guard.status != "Active",
                    Guard.status.is_(None)
                )
            )
            .count()
        )


        guard_data = pd.DataFrame(
            {
                "Status": [
                    "Active",
                    "Inactive"
                ],

                "Count": [
                    active_guards,
                    inactive_guards
                ]
            }
        )


        # ==========================================
        # SITE STATUS
        # ==========================================

        active_sites = (
            db.query(Site)
            .filter(Site.status == "Active")
            .count()
        )


        inactive_sites = (
            db.query(Site)
            .filter(
                or_(
                    Site.status != "Active",
                    Site.status.is_(None)
                )
            )
            .count()
        )


        site_data = pd.DataFrame(
            {
                "Status": [
                    "Active",
                    "Inactive"
                ],

                "Count": [
                    active_sites,
                    inactive_sites
                ]
            }
        )


        return guard_data, site_data


    finally:

        db.close()


# ==================================================
# CREATE DONUT CHART
# ==================================================

def create_status_chart(
    chart_data,
    title
):

    total = chart_data["Count"].sum()


    # ==============================================
    # NO DATA AVAILABLE
    # ==============================================

    if total == 0:

        fig = px.pie(
            names=["No Data"],
            values=[1],
            hole=0.68
        )

        fig.update_traces(
            textinfo="label",
            hoverinfo="skip"
        )


    # ==============================================
    # NORMAL DATA
    # ==============================================

    else:

        fig = px.pie(
            chart_data,
            names="Status",
            values="Count",
            hole=0.68
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )


    # ==============================================
    # LAYOUT
    # ==============================================

    fig.update_layout(

        title=dict(
            text=title,
            font=dict(
                size=18
            ),
            x=0.5,
            xanchor="center"
        ),

        showlegend=True,

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),

        height=360,

        margin=dict(
            l=20,
            r=20,
            t=60,
            b=40
        ),

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            color="#e5e7eb"
        )
    )


    return fig


# ==================================================
# DASHBOARD PAGE
# ==================================================

def show_dashboard():

    # ==============================================
    # LOAD DATA
    # ==============================================

    data = get_dashboard_data()


    # ==============================================
    # CURRENT USER
    # ==============================================

    user = st.session_state.get(
        "user",
        {}
    )

    username = user.get(
        "username",
        "User"
    )


    # ==============================================
    # HEADER
    # ==============================================

    st.markdown(
        f"""
# Welcome back, {username} 👋
"""
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

        dashboard_card(
            title="Total Guards",
            value=data["total_guards"],
            icon="👮",
            icon_class="icon-purple",
            footer=f'{data["active_guards"]} Active',
            footer_class="status-positive"
        )


    with col2:

        dashboard_card(
            title="Total Sites",
            value=data["total_sites"],
            icon="🏢",
            icon_class="icon-blue",
            footer=f'{data["active_sites"]} Active',
            footer_class="status-positive"
        )


    with col3:

        dashboard_card(
            title="Shifts Today",
            value=data["shifts_today"],
            icon="📅",
            icon_class="icon-orange",
            footer="Scheduled for today",
            footer_class="status-warning"
        )


    with col4:

        dashboard_card(
            title="Open Incidents",
            value=data["open_incidents"],
            icon="🚨",
            icon_class="icon-red",
            footer="Requires attention",
            footer_class="status-danger"
        )


    # ==============================================
    # SECONDARY STATISTICS
    # ==============================================

    st.markdown("<br>", unsafe_allow_html=True)

    inactive_guards = (
        data["total_guards"]
        - data["active_guards"]
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        dashboard_card(
            title="Check-ins Today",
            value=data["attendance_today"],
            icon="📍",
            icon_class="icon-cyan",
            footer="Today's attendance",
            footer_class="status-positive"
        )


    with col2:

        dashboard_card(
            title="System Users",
            value=data["total_users"],
            icon="👥",
            icon_class="icon-purple",
            footer="Registered users",
            footer_class=""
        )


    with col3:

        dashboard_card(
            title="Inactive Guards",
            value=inactive_guards,
            icon="⚠️",
            icon_class="icon-orange",
            footer="Not currently active",
            footer_class="status-warning"
        )


    # ==============================================
    # ANALYTICS
    # ==============================================

    st.markdown("<br>", unsafe_allow_html=True)

    st.html(
        """
<div class="dashboard-section-title">
    📊 Security Analytics
</div>
"""
    )


    # Get analytics data

    guard_chart_data, site_chart_data = (
        get_status_chart_data()
    )


    chart_col1, chart_col2 = st.columns(2)


    # ==============================================
    # GUARD STATUS CHART
    # ==============================================

    with chart_col1:

        st.html(
            """
<div class="chart-title">
    👮 Guard Status Overview
</div>
"""
        )

        fig_guards = create_status_chart(
            guard_chart_data,
            ""
        )

        st.plotly_chart(
            fig_guards,
            width="stretch",
            key="guard_status_chart"
        )


    # ==============================================
    # SITE STATUS CHART
    # ==============================================

    with chart_col2:

        st.html(
            """
<div class="chart-title">
    🏢 Site Status Overview
</div>
"""
        )

        fig_sites = create_status_chart(
            site_chart_data,
            ""
        )

        st.plotly_chart(
            fig_sites,
            width="stretch",
            key="site_status_chart"
        )


    # ==============================================
    # QUICK ACTIONS
    # ==============================================

    st.divider()

    st.html(
        """
<div class="dashboard-section-title">
    ⚡ Quick Actions
</div>
"""
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        if st.button(
            "➕ Add Guard",
            key="quick_add_guard",
            width="stretch"
        ):

            st.session_state["selected_page"] = "Guards"

            st.rerun()


    with col2:

        if st.button(
            "🏢 Add Site",
            key="quick_add_site",
            width="stretch"
        ):

            st.session_state["selected_page"] = "Sites"

            st.rerun()


    with col3:

        if st.button(
            "📅 Manage Shifts",
            key="quick_manage_shifts",
            width="stretch"
        ):

            st.session_state["selected_page"] = "Shifts"

            st.rerun()


    with col4:

        if st.button(
            "🚨 Report Incident",
            key="quick_report_incident",
            width="stretch"
        ):

            st.session_state["selected_page"] = "Incidents"

            st.rerun()