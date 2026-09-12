import streamlit as st
import time
from utils import constants

# ==================================================
# PERFORMANCE TIMER
# ==================================================
_REQUEST_START = time.perf_counter()

def perf(label, start=None):
    now = time.perf_counter()
    step = now - start if start is not None else 0
    total = now - _REQUEST_START
    print(
        f"[PERF] {label:<32} "
        f"step={step:.3f}s | total={total:.3f}s",
        flush=True,
    )
    return now
 




st.set_page_config( 
    page_title=constants.COMPANY_NAME, 
    page_icon=constants.LOGO_PATH, 
    layout="wide", 
    initial_sidebar_state="expanded" 
) 

# ================================================== 
# AUTH / PERMISSIONS 
# ================================================== 

#from utils.auth import create_default_super_admin 
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

from utils.styles import load_custom_css 
from components.sidebar import render_sidebar 

_t = perf("BEFORE load_custom_css")
load_custom_css()
perf("AFTER load_custom_css", _t) 

def restore_login_session():
    if "user" in st.session_state: 
        return 

    cookie_manager = get_cookie_manager() 

    token = cookie_manager.get(cookie="security_session") 

    if not token: 
        return 

    user_data = get_user_from_session(token) 

    if user_data: 
        st.session_state["user"] = user_data 

_t = perf("BEFORE restore_login_session")
restore_login_session()
perf("AFTER restore_login_session", _t)

if "user" not in st.session_state: 
    show_login_page() 
    st.stop() 
else: 
    print(f"User '{st.session_state['user']['username']}' is logged in.") 

user = st.session_state["user"] 

username = user.get("username", "User") 
role = user.get("role", "User") 

_t = perf("BEFORE get_allowed_pages")
allowed_pages = get_allowed_pages(role)
perf("AFTER get_allowed_pages", _t) 

_t = perf("BEFORE render_sidebar")
selected_page = render_sidebar(
    username=username,
    role=role,
    allowed_pages=allowed_pages
)
perf(f"AFTER render_sidebar [{selected_page}]", _t) 

if selected_page == "Dashboard": 
    _t = perf("BEFORE show_dashboard")
    show_dashboard()
    perf("AFTER show_dashboard", _t)

elif selected_page == "Guards": 
    _t = perf("BEFORE show_guards")
    show_guards()
    perf("AFTER show_guards", _t)

elif selected_page == "Guard Work": 
    _t = perf("BEFORE show_guard_work")
    show_guard_work()
    perf("AFTER show_guard_work", _t)

elif selected_page == "Sites": 
    _t = perf("BEFORE show_sites")
    show_sites()
    perf("AFTER show_sites", _t)

elif selected_page == "Shifts": 
    _t = perf("BEFORE show_shifts")
    show_shifts()
    perf("AFTER show_shifts", _t)

elif selected_page == "Attendance": 
    _t = perf("BEFORE show_attendance")
    show_attendance()
    perf("AFTER show_attendance", _t)

elif selected_page == "Incidents": 
    _t = perf("BEFORE show_incidents")
    show_incidents()
    perf("AFTER show_incidents", _t)

elif selected_page == "Users": 
    _t = perf("BEFORE show_users")
    show_users()
    perf("AFTER show_users", _t)

elif selected_page == "Reports": 
    _t = perf("BEFORE show_reports")
    show_reports()
    perf("AFTER show_reports", _t)

elif selected_page == "Settings": 
    _t = perf("BEFORE show_settings")
    show_settings()
    perf("AFTER show_settings", _t)

elif selected_page == "Company Settings": 
    _t = perf("BEFORE show_company_settings")
    show_company_settings()
    perf("AFTER show_company_settings", _t)

elif selected_page == "Billing & Payroll": 
    _t = perf("BEFORE show_billing_payroll")
    show_billing_payroll()
    perf("AFTER show_billing_payroll", _t)

elif selected_page == "My Shift": 
    st.title("📅 My Shift") 
    st.info("Your assigned shifts will appear here.") 

elif selected_page == "Check In / Out": 
    st.title("📍 Check In / Out") 
    st.info("Guard attendance check-in and check-out will appear here.") 

else: 
    st.warning("You do not have permission to access this page.") 

perf(f"REQUEST COMPLETE [{selected_page}]")
