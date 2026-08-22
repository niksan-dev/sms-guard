import streamlit as st


# ==================================================
# PAGE ICONS
# ==================================================

PAGE_ICONS = {
    "Dashboard": "📊",
    "Guards": "👮",
    "Sites": "🏢",
    "Shifts": "📅",
    "Attendance": "🟢",
    "Incidents": "🚨",
    "Users": "👥",
    "Reports": "📊",
    "Settings": "⚙️",
    "Company Settings": "🏢",
    "My Shift": "📅",
    "Check In / Out": "📍",
}


# ==================================================
# ROLE DISPLAY NAME
# ==================================================

def get_display_role(role):

    role_names = {
        "Super Admin": "Super Admin",
        "Admin": "Administrator",
        "Manager": "Manager",
        "Supervisor": "Supervisor",
        "Security Guard": "Security Guard",
        "Client": "Client",
    }

    return role_names.get(role, role)


# ==================================================
# SIDEBAR
# ==================================================

def render_sidebar(username, role, allowed_pages):

    with st.sidebar:

        # ==========================================
        # BRAND
        # ==========================================

        col1, col2 = st.columns(
            [1, 4],
            vertical_alignment="center"
        )

        with col1:
            st.markdown("## 🛡️")

        with col2:
            st.markdown("### Pravin Mokal Enterprises")
            st.caption("SECURITY GUARD MANAGEMENT SYSTEM")


        st.divider()


        # ==========================================
        # NAVIGATION TITLE
        # ==========================================

        st.caption("NAVIGATION")


        # ==========================================
        # VALIDATE ALLOWED PAGES
        # ==========================================

        if not allowed_pages:

            st.error(
                "No pages are assigned to this role."
            )

            return None


        # ==========================================
        # INITIALIZE SELECTED PAGE
        # ==========================================

        if "selected_page" not in st.session_state:

            st.session_state["selected_page"] = (
                allowed_pages[0]
            )


        # Make sure selected page belongs to this role
        if (
            st.session_state["selected_page"]
            not in allowed_pages
        ):

            st.session_state["selected_page"] = (
                allowed_pages[0]
            )


        # ==========================================
        # NAVIGATION
        # ==========================================

        navigation_options = []

        for page in allowed_pages:

            icon = PAGE_ICONS.get(page, "📄")

            navigation_options.append(
                f"{icon}  {page}"
            )


        # Get currently selected index
        current_index = allowed_pages.index(
            st.session_state["selected_page"]
        )


        # Navigation radio
        selected_option = st.radio(
            label="Navigation",
            options=navigation_options,
            index=current_index,
            key="sidebar_navigation",
            label_visibility="collapsed"
        )


        # Get selected index
        selected_index = navigation_options.index(
            selected_option
        )


        # Save actual page name
        selected_page = allowed_pages[selected_index]

        st.session_state["selected_page"] = (
            selected_page
        )


        # ==========================================
        # DIVIDER
        # ==========================================

        st.divider()


        # ==========================================
        # USER PROFILE
        # ==========================================

        display_role = get_display_role(role)


        user_col1, user_col2 = st.columns(
            [1, 3],
            vertical_alignment="center"
        )


        with user_col1:

            st.markdown("# 👤")


        with user_col2:

            st.markdown(
                f"**{username}**"
            )

            st.caption(
                display_role
            )


        # ==========================================
        # LOGOUT
        # ==========================================

        st.divider()


        if st.button(
            "🚪 Logout",
            key="logout_button",
            use_container_width=True
        ):

            st.session_state["user"] = None

            st.session_state.pop(
                "selected_page",
                None
            )

            st.session_state.pop(
                "sidebar_navigation",
                None
            )

            st.rerun()


        # ==========================================
        # RETURN SELECTED PAGE
        # ==========================================

        return selected_page