import streamlit as st

# ==================================================
# AUTH / PERMISSIONS
# ==================================================

from utils.auth import create_default_super_admin
from utils.permissions import get_allowed_pages


# ==================================================
# VIEWS
# ==================================================

from views.login import show_login_page
from views.dashboard import show_dashboard
from views.guards import show_guards
from views.sites import show_sites
from views.shifts import show_shifts
from views.attendance import show_attendance
from views.incidents import show_incidents
from views.users import show_users
from views.reports import show_reports
from views.settings import show_settings
from views.payments import show_payments

from views.company_settings import show_company_settings


# ==================================================
# UI COMPONENTS
# ==================================================

from utils.styles import load_custom_css
from components.sidebar import render_sidebar


# ==================================================
# PAGE CONFIGURATION
# IMPORTANT: MUST BE THE FIRST STREAMLIT COMMAND
# ==================================================

st.set_page_config(
    page_title="Pravin Mokal Enterprises",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# LOAD GLOBAL STYLES
# ==================================================

load_custom_css()


# ==================================================
# DATABASE INITIALIZATION
# ==================================================

# Create default Super Admin if it does not exist
create_default_super_admin()


# ==================================================
# SESSION INITIALIZATION
# ==================================================

if "user" not in st.session_state:
    st.session_state["user"] = None


# ==================================================
# AUTHENTICATION CHECK
# ==================================================

if not st.session_state["user"]:

    show_login_page()

    # Do not show sidebar or application pages
    st.stop()


# ==================================================
# CURRENT LOGGED-IN USER
# ==================================================

user = st.session_state["user"]

username = user.get("username", "User")
role = user.get("role", "User")


# ==================================================
# ROLE-BASED PAGE ACCESS
# ==================================================

allowed_pages = get_allowed_pages(role)


# ==================================================
# SIDEBAR NAVIGATION
# ==================================================

selected_page = render_sidebar(
    username=username,
    role=role,
    allowed_pages=allowed_pages
)


# ==================================================
# PAGE ROUTING
# ==================================================

if selected_page == "Dashboard":

    show_dashboard()


elif selected_page == "Guards":

    show_guards()


elif selected_page == "Sites":

    show_sites()


elif selected_page == "Shifts":

    show_shifts()


elif selected_page == "Attendance":

    show_attendance()


elif selected_page == "Incidents":

    show_incidents()


elif selected_page == "Users":

    show_users()


elif selected_page == "Reports":

    show_reports()


elif selected_page == "Settings":

    show_settings()

elif selected_page == "Company Settings":

    show_company_settings()

elif selected_page == "Payments":

    show_payments()


# ==================================================
# SECURITY GUARD ROUTES
# ==================================================

elif selected_page == "My Shift":

    st.title("📅 My Shift")

    st.info(
        "Your assigned shifts will appear here."
    )


elif selected_page == "Check In / Out":

    st.title("📍 Check In / Out")

    st.info(
        "Guard attendance check-in and check-out will appear here."
    )


# ==================================================
# FALLBACK
# ==================================================

else:

    st.warning(
        "You do not have permission to access this page."
    )