import streamlit as st
import pandas as pd

from utils.constants import UserRole

from services.user_service import (
    get_all_users,
    create_user,
    update_user_role,
    update_user_status,
    update_user_profile
)


def show_users():

    st.title("👥 User Management")

    st.caption(
        "Manage system users, roles, and account access."
    )

    tab1, tab2, tab3 = st.tabs([
        "👥 All Users",
        "➕ Add User",
        "⚙️ Manage User"
    ])

    # ==================================================
    # ALL USERS
    # ==================================================

    # ==================================================
# ALL USERS
# ==================================================

    with tab1:

        users = get_all_users()

        if not users:

            st.info("No users found.")

        else:

            user_data = []

            for user in users:

                user_data.append({
                    "ID": user.id,
                    "Username": user.username,
                    "Email": user.email or "",
                    "Phone": user.phone or "",
                    "Role": user.role,
                    "Status": (
                        "Active"
                        if user.is_active
                        else "Inactive"
                    ),
                    "Created At": user.created_at
                })

            df = pd.DataFrame(user_data)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

    # ==================================================
    # ADD USER
    # ==================================================

    with tab2:

        st.subheader("➕ Create New User")

        with st.form("create_user_form"):

            # ----------------------------------------------
            # USERNAME
            # ----------------------------------------------

            username = st.text_input(
                "Username"
            )

            # ----------------------------------------------
            # EMAIL
            # ----------------------------------------------

            email = st.text_input(
                "Email"
            )

            # ----------------------------------------------
            # PHONE
            # ----------------------------------------------

            phone = st.text_input(
                "Phone"
            )

            # ----------------------------------------------
            # ROLE
            # ----------------------------------------------

            role = st.selectbox(
                "Role",
                [
                    UserRole.ADMIN_MANAGER.value,
                    UserRole.SUPERVISOR.value,
                    UserRole.SECURITY_GUARD.value,
                    UserRole.CLIENT.value
                ]
            )

            # ----------------------------------------------
            # PASSWORD
            # ----------------------------------------------

            password = st.text_input(
                "Password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Create User",
                use_container_width=True
            )

        if submitted:

            if not username:

                st.warning(
                    "Username is required."
                )

            elif not password:

                st.warning(
                    "Password is required."
                )

            elif len(password) < 6:

                st.warning(
                    "Password must contain at least 6 characters."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                success, message = create_user(
                    username=username.strip(),
                    password=password,
                    email=email,
                    phone=phone,
                    role=role
                )

                if success:

                    st.success(message)
                    st.rerun()

                else:

                    st.error(message)

    # ==================================================
    # MANAGE USER
    # ==================================================

    # ==================================================
# MANAGE USER
# ==================================================

    with tab3:

        users = get_all_users()

        if not users:

            st.info("No users available.")

        else:

            # ----------------------------------------------
            # SELECT USER
            # ----------------------------------------------

            user_options = {
                f"{user.id} - {user.username} ({user.role})": user
                for user in users
            }

            selected_label = st.selectbox(
                "Select User",
                list(user_options.keys()),
                key="manage_user_select"
            )

            selected_user = user_options[selected_label]

            st.divider()

            # ==============================================
            # EDIT PROFILE
            # ==============================================

            st.subheader("✏️ Edit Profile")

            with st.form(
                f"edit_user_form_{selected_user.id}"
            ):

                edit_username = st.text_input(
                    "Username",
                    value=selected_user.username
                )

                edit_email = st.text_input(
                    "Email",
                    value=selected_user.email or ""
                )

                edit_phone = st.text_input(
                    "Phone",
                    value=selected_user.phone or ""
                )

                update_profile_clicked = st.form_submit_button(
                    "💾 Save Profile Changes",
                    use_container_width=True
                )

            if update_profile_clicked:

                if not edit_username.strip():

                    st.warning(
                        "Username is required."
                    )

                else:

                    success, message = update_user_profile(
                        user_id=selected_user.id,
                        username=edit_username,
                        email=edit_email,
                        phone=edit_phone
                    )

                    if success:

                        st.success(message)
                        st.rerun()

                    else:

                        st.error(message)


            st.divider()


            # ==============================================
            # ROLE AND STATUS
            # ==============================================

            col1, col2 = st.columns(2)


            # ----------------------------------------------
            # CHANGE ROLE
            # ----------------------------------------------

            with col1:

                st.subheader("🔄 Change Role")

                role_values = [
                    role.value
                    for role in UserRole
                ]

                # Get current role index safely
                current_role_index = (
                    role_values.index(selected_user.role)
                    if selected_user.role in role_values
                    else 0
                )

                new_role = st.selectbox(
                    "User Role",
                    role_values,
                    index=current_role_index,
                    key=f"user_role_{selected_user.id}"
                )

                if st.button(
                    "Update Role",
                    use_container_width=True,
                    key=f"update_role_{selected_user.id}"
                ):

                    success, message = update_user_role(
                        selected_user.id,
                        new_role
                    )

                    if success:

                        st.success(message)
                        st.rerun()

                    else:

                        st.error(message)


            # ----------------------------------------------
            # ACCOUNT STATUS
            # ----------------------------------------------

            with col2:

                st.subheader("🔐 Account Status")

                current_status = (
                    "🟢 Active"
                    if selected_user.is_active
                    else "🔴 Inactive"
                )

                st.write(
                    f"Current status: **{current_status}**"
                )

                if selected_user.is_active:

                    if st.button(
                        "🔴 Deactivate User",
                        use_container_width=True,
                        key=f"deactivate_{selected_user.id}"
                    ):

                        success, message = update_user_status(
                            selected_user.id,
                            False
                        )

                        if success:

                            st.success(message)
                            st.rerun()

                        else:

                            st.error(message)

                else:

                    if st.button(
                        "🟢 Activate User",
                        use_container_width=True,
                        key=f"activate_{selected_user.id}"
                    ):

                        success, message = update_user_status(
                            selected_user.id,
                            True
                        )

                        if success:

                            st.success(message)
                            st.rerun()

                        else:

                            st.error(message)