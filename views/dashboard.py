import streamlit as st
from datetime import date
import calendar
from sqlalchemy import or_, func, case
from sqlalchemy.orm import joinedload

import plotly.express as px
import pandas as pd

from sqlalchemy import or_

from database.connection import SessionLocal
from database.models import User
from database.models import Guard
from database.models import Site
from database.payment import Payment
from database.guard_daily_work import GuardDailyWork

from components.page_header import page_header
from components.sub_header import sub_header
from components.button import button
# ==================================================
# OPTIONAL MODELS
# ==================================================

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

# ==================================================
# DASHBOARD CARD
# ==================================================

def dashboard_card(
    title,
    value,
    icon,
    icon_class="",
    footer="",
    footer_class="",
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
# DASHBOARD DATA CACHE
# ==================================================

# Dashboard values are operational summaries. A short cache avoids
# repeating the same Supabase queries on every Streamlit rerun while
# keeping the dashboard effectively near-real-time.
DASHBOARD_CACHE_TTL = 15


# ==================================================
# GET DASHBOARD DATA
# ==================================================

@st.cache_data(
    ttl=DASHBOARD_CACHE_TTL,
    max_entries=8,
    show_spinner=False,
)
def get_dashboard_data():

    db = SessionLocal()

    try:

        today = date.today()

        # ==========================================
        # GUARDS + MONTHLY SALARY
        # ==========================================
        #
        # Previously these were 3 separate database
        # round-trips. One aggregate query is enough.

        guard_stats = (
            db.query(
                func.count(Guard.id),
                func.coalesce(
                    func.sum(
                        case(
                            (Guard.status == "Active", 1),
                            else_=0,
                        )
                    ),
                    0,
                ),
                func.coalesce(
                    func.sum(Guard.monthly_salary),
                    0,
                ),
            )
            .first()
        )

        total_guards = int(guard_stats[0] or 0)
        active_guards = int(guard_stats[1] or 0)
        total_guard_salary = float(guard_stats[2] or 0)

        # ==========================================
        # SITES
        # ==========================================
        #
        # Total sites, active sites and expected
        # collection are obtained in one query.

        site_stats = (
            db.query(
                func.count(Site.id),
                func.coalesce(
                    func.sum(
                        case(
                            (Site.status == "Active", 1),
                            else_=0,
                        )
                    ),
                    0,
                ),
                func.coalesce(
                    func.sum(
                        Site.guards_required * Site.guard_rate
                    ),
                    0,
                ),
            )
            .first()
        )

        total_sites = int(site_stats[0] or 0)
        active_sites = int(site_stats[1] or 0)
        total_site_collection = float(site_stats[2] or 0)

        # ==========================================
        # PAYMENT COLLECTION
        # ==========================================

        total_collected = 0.0

        if hasattr(Payment, "amount"):

            payment_query = db.query(Payment)

            if hasattr(Payment, "status"):

                payment_query = payment_query.filter(
                    Payment.status.in_(
                        [
                            "Paid",
                            "Completed",
                            "Collected",
                        ]
                    )
                )

            total_collected = (
                payment_query
                .with_entities(
                    func.coalesce(
                        func.sum(Payment.amount),
                        0,
                    )
                )
                .scalar()
                or 0
            )

        total_collected = float(total_collected)

        # ==========================================
        # PENDING COLLECTION
        # ==========================================

        total_pending = max(
            0,
            total_site_collection - total_collected,
        )

        # ==========================================
        # USERS
        # ==========================================

        total_users = int(
            db.query(func.count(User.id)).scalar() or 0
        )

        # ==========================================
        # SHIFTS / TODAY'S GUARD WORK
        # ==========================================
        #
        # GuardDailyWork already represents today's guard-shift records.
        # Load it once and derive both today's shift count and financials
        # instead of making a separate Shift query plus two more attendance
        # queries.

        daily_guard_salary = 0.0
        daily_site_revenue = 0.0
        shifts_today = 0

        try:
            total_days_in_month = calendar.monthrange(
                today.year,
                today.month,
            )[1]

            daily_records = (
                db.query(GuardDailyWork)
                .options(
                    joinedload(GuardDailyWork.guard),
                    joinedload(GuardDailyWork.site),
                )
                .filter(GuardDailyWork.work_date == today)
                .all()
            )

            shifts_today = len(daily_records)

            for record in daily_records:
                if record.status != "Present":
                    continue

                guard = record.guard
                site = record.site

                if guard:
                    monthly_salary = float(guard.monthly_salary or 0)
                    daily_guard_salary += (
                        monthly_salary / total_days_in_month
                        if total_days_in_month > 0
                        else 0.0
                    )

                if site:
                    guard_rate = float(site.guard_rate or 0)
                    daily_site_revenue += (
                        guard_rate / total_days_in_month
                        if total_days_in_month > 0
                        else 0.0
                    )

        except Exception:
            # Preserve the dashboard's previous safe-fallback behavior.
            daily_guard_salary = 0.0
            daily_site_revenue = 0.0
            shifts_today = 0

        # ==========================================
        # OPEN INCIDENTS
        # ==========================================

        open_incidents = 0

        if (
            Incident
            and hasattr(Incident, "status")
        ):

            open_incidents = int(
                db.query(func.count(Incident.id))
                .filter(
                    Incident.status.in_(
                        [
                            "Open",
                            "In Progress",
                        ]
                    )
                )
                .scalar()
                or 0
            )

        # ==========================================
        # ATTENDANCE TODAY
        # ==========================================

        attendance_today = 0

        if Attendance:

            if hasattr(Attendance, "check_in"):

                attendance_today = int(
                    db.query(func.count(Attendance.id))
                    .filter(
                        Attendance.check_in >= today
                    )
                    .scalar()
                    or 0
                )

        # ==========================================
        # RETURN DATA
        # ==========================================

        total_profit_today = (
            daily_site_revenue - daily_guard_salary
        )

        return {
            # Guards
            "total_guards": total_guards,
            "active_guards": active_guards,
            "total_guard_salary": total_guard_salary,

            "total_profit_today": total_profit_today,

            # Sites
            "total_sites": total_sites,
            "active_sites": active_sites,

            # Collections
            "total_site_collection": total_site_collection,
            "total_collected": total_collected,
            "total_pending": total_pending,

            # Users
            "total_users": total_users,

            # Operations
            "shifts_today": shifts_today,
            "open_incidents": open_incidents,
            "attendance_today": attendance_today,

            # Today's work financials
            "daily_guard_salary": daily_guard_salary,
            "daily_site_revenue": daily_site_revenue,
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
    #return
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
    # PAGE HEADER
    # ==============================================

    page_header(f"Welcome back, {username}","Here's what's happening with your security operations today.")



    # ==============================================
    # PRIMARY STATISTICS
    # ==============================================

    col1, col2 = st.columns(2)


    with col1:

        dashboard_card(
            title="Total Guards",
            value=data["total_guards"],
            icon="👮",
            icon_class="icon-blue",
            footer=f'{data["active_guards"]} Active',
            footer_class="status-positive",
        )


    with col2:

        dashboard_card(
            title="Total Sites",
            value=data["total_sites"],
            icon="🏢",
            icon_class="icon-blue",
            footer=f'{data["active_sites"]} Active',
            footer_class="status-positive",
        )


    # ==============================================
    # TODAY'S OPERATIONS
    # ==============================================

    sub_header("Today's Operations","","📅")


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        dashboard_card(
            title="Shifts Today",
            value=data["shifts_today"],
            icon="📅",
            icon_class="icon-orange",
            footer="Recorded for today",
            footer_class="status-warning",
        )


    with col2:

        dashboard_card(
            title="Daily Guard Salary",
            value=f'₹ {data["daily_guard_salary"]:,.2f}',
            icon="👮",
            icon_class="icon-red",
            footer="Salary from today's shifts",
            footer_class="status-danger",
        )


    with col3:

        dashboard_card(
            title="Daily Site Revenue",
            value=f'₹ {data["daily_site_revenue"]:,.2f}',
            icon="💰",
            icon_class="icon-cyan",
            footer="Revenue from today's shifts",
            footer_class="status-positive",
        )


    with col4:

        dashboard_card(
            title="Today's Profit",
            value=f'₹ {data["total_profit_today"]:,.2f}',
            icon="💸",
            icon_class="icon-cyan",
            footer="Profit from today's shifts",
            footer_class="status-positive",
        )


    # ==============================================
    # FINANCIAL OVERVIEW
    # ==============================================


    sub_header("Financial Overview","","💰")


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        dashboard_card(
            title="Guard Salary",
            value=f'₹ {data["total_guard_salary"]:,.0f}',
            icon="👮",
            icon_class="icon-red",
            footer="Total monthly salary",
            footer_class="status-danger",
        )


    with col2:

        dashboard_card(
            title="Total Collection",
            value=f'₹ {data["total_site_collection"]:,.0f}',
            icon="💰",
            icon_class="icon-blue",
            footer="Expected monthly collection",
            footer_class="status-positive",
        )


    with col3:

        dashboard_card(
            title="Collected",
            value=f'₹ {data["total_collected"]:,.0f}',
            icon="✅",
            icon_class="icon-cyan",
            footer="Amount received",
            footer_class="status-positive",
        )


    with col4:

        dashboard_card(
            title="Pending",
            value=f'₹ {data["total_pending"]:,.0f}',
            icon="⏳",
            icon_class="icon-orange",
            footer="Amount yet to collect",
            footer_class="status-warning",
        )


    # # ==============================================
    # # SECURITY ANALYTICS
    # # ==============================================
    # sub_header("Security Analytics","","📊")


    # guard_chart_data, site_chart_data = (
    #     get_status_chart_data()
    # )


    # chart_col1, chart_col2 = st.columns(2)


    # # ==============================================
    # # GUARD STATUS
    # # ==============================================

    # with chart_col1:

    #     st.html(
    #         """
    #         <div class="dashboard-chart-card">

    #             <div class="chart-title">
    #                 👮 Guard Status Overview
    #             </div>

    #         </div>
    #         """
    #     )


    #     fig_guards = create_status_chart(
    #         guard_chart_data,
    #         "",
    #     )


    #     st.plotly_chart(
    #         fig_guards,
    #         width="stretch",
    #         key="guard_status_chart",
    #     )


    # # ==============================================
    # # SITE STATUS
    # # ==============================================

    # with chart_col2:

    #     st.html(
    #         """
    #         <div class="dashboard-chart-card">

    #             <div class="chart-title">
    #                 🏢 Site Status Overview
    #             </div>

    #         </div>
    #         """
    #     )


    #     fig_sites = create_status_chart(
    #         site_chart_data,
    #         "",
    #     )


    #     st.plotly_chart(
    #         fig_sites,
    #         width="stretch",
    #         key="site_status_chart",
    #     )


    # ==============================================
    # QUICK ACTIONS
    # ==============================================
    sub_header("Quick Actions","","⚡")


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        if button(
            "➕ Add Guard",
            key="quick_add_guard",
            width="stretch",
            type="primary",
        ):

            st.session_state["selected_page"] = "Guards"

            st.rerun()


    with col2:

        if button(
            "🏢 Add Site",
            key="quick_add_site",
            width="stretch",
            type="primary",
        ):

            st.session_state["selected_page"] = "Sites"

            st.rerun()


    with col3:

        if button(
            "📅 Manage Shifts",
            key="quick_manage_shifts",
            width="stretch",
            type="primary",
        ):

            st.session_state["selected_page"] = "Shifts"

            st.rerun()


    with col4:

        if button(
            "🚨 Report Incident",
            key="quick_report_incident",
            width="stretch",
            type="primary",
        ):

            st.session_state["selected_page"] = "Incidents"

            st.rerun()