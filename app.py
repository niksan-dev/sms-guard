import streamlit as st
from utils import constants




st.set_page_config(
    page_title=constants.COMPANY_NAME,
    page_icon=constants.LOGO_PATH,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# AUTH / PERMISSIONS
# ==================================================

from utils.auth import create_default_super_admin
from utils.permissions import get_allowed_pages

from utils.cookies import get_cookie_manager
from services.auth_session_service import (
    get_user_from_session
)

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
from views.guard_work import show_guard_work
from views.company_settings import show_company_settings
from views.guard_work import show_guard_work
from views.billing_payroll import show_billing_payroll

# from database.connection import engine
# from sqlalchemy import text

# with engine.connect() as connection:
#     connection.execute(text("DROP TABLE IF EXISTS guard_work_logs"))
#     connection.commit()

# ==================================================
# UI COMPONENTS
# ==================================================
from utils.styles import load_custom_css
from components.sidebar import render_sidebar

#=================================================
# Global styles and configurations
#=================================================

#from utils.global_style import apply_global_styles
# ==================================================
# PAGE CONFIGURATION
# IMPORTANT: MUST BE THE FIRST STREAMLIT COMMAND
# ==================================================


load_custom_css()
#apply_global_styles()
def restore_login_session():

    # User already restored
    if "user" in st.session_state:
        return

    cookie_manager = get_cookie_manager()

    token = cookie_manager.get(
        cookie="security_session"
    )

    if not token:
        return

    user_data = get_user_from_session(token)

    if user_data:

        st.session_state["user"] = user_data


restore_login_session()
# ==================================================
# LOAD GLOBAL STYLES
# ==================================================




# ==================================================
# DATABASE INITIALIZATION
# ==================================================

# Create default Super Admin if it does not exist
create_default_super_admin()


# ==================================================
# SESSION INITIALIZATION
# ==================================================

# if "user" not in st.session_state:
#     st.session_state["user"] = None


# ==================================================
# AUTHENTICATION CHECK
# ==================================================
#print(f"User '{st.session_state['user']}'")

# if not st.session_state["user"]:

#     show_login_page()

#     # Do not show sidebar or application pages
#     st.stop()

# else:
#     print(
#         f"User '{st.session_state['user']['username']}' is logged in."
#     )


if "user" not in st.session_state:

    show_login_page()

    st.stop()
else:
    
    print(
        f"User '{st.session_state['user']['username']}' is logged in."
    )
    


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

elif selected_page == "Guard Work":
   #print("Guard Work page selected")

    show_guard_work()


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

elif selected_page == "Billing & Payroll":

    show_billing_payroll()


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


