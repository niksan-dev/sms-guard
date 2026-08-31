import os
from pathlib import Path

import streamlit as st

from services.auth_session_service import delete_login_session
from utils.cookies import get_cookie_manager
from utils import constants
from components.button import button


# =========================================================
# PAGE ICONS
# =========================================================

PAGE_ICONS = {
    "Dashboard": "📊",
    "Guards": "👮",
    "Sites": "🏢",
    "Shifts": "📅",
    "Billing & Payroll": "💳",
    "Attendance": "🟢",
    "Incidents": "🚨",
    "Users": "👥",
    "Reports": "📊",
    "Settings": "⚙️",
    "Company Settings": "🏢",
    "My Shift": "📅",
    "Check In / Out": "📍",
}


# =========================================================
# ROLE DISPLAY NAME
# =========================================================

def get_display_role(role):

    role_names = {
        "Super Admin": "Super Admin",
        "Admin": "Administrator",
        "Manager": "Manager",
        "Supervisor": "Supervisor",
        "Security Guard": "Security Guard",
        "Client": "Client",
    }

    return role_names.get(
        role,
        role,
    )


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# =========================================================
# COMPANY LOGO
# =========================================================

logo_path = os.path.join(
    BASE_DIR,
    "uploads",
    "company",
    "company_logo.png",
)


# =========================================================
# CSS
# =========================================================

_CSS_LOADED = False


def _load_sidebar_css():

    css_path = (
        Path(__file__).resolve().parent.parent
        / "css"
        / "sidebar.css"
    )

    if not css_path.exists():
        raise FileNotFoundError(
            f"Sidebar CSS not found: {css_path}"
        )

    css = css_path.read_text(
        encoding="utf-8"
    )

    st.markdown(
        f"<style id='security-sidebar-css'>{css}</style>",
        unsafe_allow_html=True,
    )


# =========================================================
# SIDEBAR
# =========================================================

def render_sidebar(
    username,
    role,
    allowed_pages,
):

    # =====================================================
    # LOAD CSS
    # =====================================================

    _load_sidebar_css()


    # =====================================================
    # VALIDATE ALLOWED PAGES
    # =====================================================

    if not allowed_pages:

        with st.sidebar:

            st.error(
                "No pages are assigned to this role."
            )

        return None


    # =====================================================
    # INITIALIZE SELECTED PAGE
    # =====================================================

    if "selected_page" not in st.session_state:

        st.session_state[
            "selected_page"
        ] = allowed_pages[0]


    # =====================================================
    # VALIDATE SELECTED PAGE
    # =====================================================

    if (
        st.session_state[
            "selected_page"
        ]
        not in allowed_pages
    ):

        st.session_state[
            "selected_page"
        ] = allowed_pages[0]


    # =====================================================
    # SIDEBAR
    # =====================================================

    with st.sidebar:

        # =================================================
        # BRAND
        # =================================================

        brand_col1, brand_col2 = st.columns(
            [4, 5],
            vertical_alignment="center",
        )


        with brand_col1:

            if os.path.exists(logo_path):

                st.image(
                    logo_path,
                    width=120,
                )


        with brand_col2:

            st.markdown(
                f"""
                <div class="sidebar-brand-title">
                    {constants.COMPANY_NAME}
                </div>
                """,
                unsafe_allow_html=True,
            )


        # =================================================
        # DESCRIPTION
        # =================================================

        st.markdown(
            f"""
            <div class="sidebar-brand-description">
                {constants.DESCRIPTION}
            </div>
            """,
            unsafe_allow_html=True,
        )


        # =================================================
        # DIVIDER
        # =================================================

        st.divider()


        # =================================================
        # NAVIGATION TITLE
        # =================================================

        st.markdown(
            """
            <div class="sidebar-navigation-title">
                NAVIGATION
            </div>
            """,
            unsafe_allow_html=True,
        )


        # =================================================
        # NAVIGATION
        # =================================================

        for page in allowed_pages:

            icon = PAGE_ICONS.get(
                page,
                "📄",
            )


            is_selected = (
                page
                == st.session_state[
                    "selected_page"
                ]
            )


            # ---------------------------------------------
            # Button type
            # ---------------------------------------------

            button_type = (
                "primary"
                if is_selected
                else "secondary"
            )


            # ---------------------------------------------
            # Navigation button
            # ---------------------------------------------

            clicked = st.button(
                f"{icon}  {page}",
                key=f"sidebar_nav_{page}",
                type=button_type,
                width="stretch",
            )


            # ---------------------------------------------
            # Change page
            # ---------------------------------------------

            if clicked:

                st.session_state[
                    "selected_page"
                ] = page

                st.rerun()


        # =================================================
        # DIVIDER
        # =================================================

        st.divider()


        # =================================================
        # USER PROFILE
        # =================================================

        display_role = get_display_role(
            role
        )


        user_col1, user_col2 = st.columns(
            [1, 3],
            vertical_alignment="center",
        )


        with user_col1:

            st.markdown(
                """
                <div class="sidebar-user-icon">
                    👤
                </div>
                """,
                unsafe_allow_html=True,
            )


        with user_col2:

            st.markdown(
                f"""
                <div class="sidebar-username">
                    {username}
                </div>
                """,
                unsafe_allow_html=True,
            )


            st.markdown(
                f"""
                <div class="sidebar-role">
                    {display_role}
                </div>
                """,
                unsafe_allow_html=True,
            )


        # =================================================
        # DIVIDER
        # =================================================

        st.divider()


        # =================================================
        # LOGOUT
        # =================================================

        logout_clicked = button(
            "🚪  Logout",
            key="sidebar_logout",
            type="primary",
            width="stretch",
        )


        if logout_clicked:

            # ---------------------------------------------
            # Cookie manager
            # ---------------------------------------------

            cookie_manager = (
                get_cookie_manager()
            )


            # ---------------------------------------------
            # Get session token
            # ---------------------------------------------

            token = cookie_manager.get(
                cookie="security_session"
            )


            # ---------------------------------------------
            # Delete database session
            # ---------------------------------------------

            if token:

                delete_login_session(
                    token
                )


            # ---------------------------------------------
            # Delete browser cookie
            # ---------------------------------------------

            cookie_manager.delete(
                "security_session"
            )


            # ---------------------------------------------
            # Clear Streamlit session
            # ---------------------------------------------

            st.session_state.clear()


            # ---------------------------------------------
            # Reload application
            # ---------------------------------------------

            st.rerun()


    # =====================================================
    # RETURN SELECTED PAGE
    # =====================================================

    return st.session_state[
        "selected_page"
    ]