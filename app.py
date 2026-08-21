import streamlit as st

#from database.connection import Base, engine
from utils.auth import create_default_super_admin
from utils.permissions import get_allowed_pages

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


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="SecureGuard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# DATABASE INITIALIZATION
# ==================================================

# Create all database tables if they do not exist
#Base.metadata.create_all(bind=engine)

# Create the default Super Admin if one does not exist
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

    # Stop here so the rest of the application
    # is not shown before login
    st.stop()


# ==================================================
# CURRENT LOGGED-IN USER
# ==================================================

user = st.session_state["user"]

username = user["username"]
role = user["role"]


# ==================================================
# GET ALLOWED PAGES FOR ROLE
# ==================================================

allowed_pages = get_allowed_pages(role)


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.markdown("# 🛡️ SecureGuard")

    st.caption(
        "Security Guard Management System"
    )

    st.divider()


    # ----------------------------------------------
    # USER INFORMATION
    # ----------------------------------------------

    st.markdown(
        f"### 👤 {username}"
    )

    st.caption(
        f"Role: {role}"
    )

    st.divider()


    # ----------------------------------------------
    # NAVIGATION
    # ----------------------------------------------

    selected_page = st.radio(
        "Navigation",
        allowed_pages
    )


    # ----------------------------------------------
    # LOGOUT
    # ----------------------------------------------

    st.divider()

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state["user"] = None

        st.rerun()


# ==================================================
# PAGE ROUTING
# ==================================================

if selected_page == "Dashboard":

    show_dashboard()


elif selected_page == "Guards":

    show_guards()


elif selected_page == "Sites":

   # show_sites()
   show_sites()
   print("Sites page is under development.")


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