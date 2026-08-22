import streamlit as st

from utils.auth import (
    authenticate_user,
    create_user
)

from utils.constants import UserRole


def show_login_page():

    # ------------------------------------------
    # Center Layout
    # ------------------------------------------

    left, center, right = st.columns([1, 1.3, 1])

    with center:

        # ------------------------------------------
        # Branding
        # ------------------------------------------

        st.markdown("# 🛡️ Pravin Mokal Enterprises")

        st.caption(
            "Security Guard Management System"
        )

        st.divider()


        # ------------------------------------------
        # Login / Signup Tabs
        # ------------------------------------------

        login_tab, signup_tab = st.tabs([
            "🔐 Login",
            "📝 Sign Up"
        ])


        # ==========================================
        # LOGIN
        # ==========================================

        with login_tab:

            st.markdown("### Welcome Back")

            with st.form("login_form"):

                username = st.text_input(
                    "Username",
                    placeholder="Enter your username"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password"
                )

                login_clicked = st.form_submit_button(
                    "🔐 Login",
                    use_container_width=True
                )


            if login_clicked:

                if not username or not password:

                    st.warning(
                        "Please enter username and password."
                    )

                else:

                    user = authenticate_user(
                        username=username.strip(),
                        password=password
                    )

                    if not user:

                        st.error(
                            "Invalid username or password."
                        )

                    else:

                        st.session_state["user"] = {
                            "id": user.id,
                            "username": user.username,
                            "role": user.role
                        }

                        st.success(
                            f"Welcome, {user.username}!"
                        )

                        st.rerun()


        # ==========================================
        # SIGN UP
        # ==========================================

        with signup_tab:

            st.markdown("### Create an Account")

            st.caption(
                "Create an account to access the SecureGuard system."
            )


            with st.form("signup_form"):

                new_role = st.selectbox(
                    "Register As",
                    [
                        UserRole.CLIENT.value,
                        UserRole.SECURITY_GUARD.value
                    ]
                )

                new_username = st.text_input(
                    "Username",
                    placeholder="Choose a username"
                )

                new_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Create a password"
                )

                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Confirm your password"
                )


                signup_clicked = st.form_submit_button(
                    "📝 Create Account",
                    use_container_width=True
                )


            if signup_clicked:

                # ----------------------------------
                # Validation
                # ----------------------------------

                if not new_username:

                    st.warning(
                        "Please enter a username."
                    )

                elif not new_password:

                    st.warning(
                        "Please enter a password."
                    )

                elif new_password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )

                elif len(new_password) < 6:

                    st.warning(
                        "Password must contain at least 6 characters."
                    )

                else:

                    # ----------------------------------
                    # Create Client Account
                    # ----------------------------------

                    user, error = create_user(
                        username=new_username.strip(),
                        password=new_password,
                        role=new_role
                    )

                    if error:

                        st.error(error)

                    else:

                        st.success(
                            "Account created successfully! "
                            "You can now log in."
                        )

