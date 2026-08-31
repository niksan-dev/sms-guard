import streamlit as st
import os

from utils.auth import (
    authenticate_user,
    create_user
)

import utils.constants as constants
from utils.constants import UserRole

from components.text_input import text_input
from components.select_box import select_box
from components.submit_button import submit_button

from services.auth_session_service import (
    create_login_session
)

from utils.cookies import get_cookie_manager


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
    "company_logo.png"
)


# =========================================================
# LOGIN PAGE
# =========================================================

def show_login_page():

    # =====================================================
    # LOGIN PAGE CSS
    # =====================================================

    st.markdown(
        """
        <style>

        /* =================================================
           LOGIN BRAND
           ================================================= */

        .login-brand-title {
            font-size: 42px;
            font-weight: 700;
            color: #063552;
            line-height: 1.1;
            letter-spacing: 0.5px;
            text-align: center;
        }


        .login-brand-description {
            margin-top: 12px;
            margin-bottom: 20px;
            color: #66839A;
            font-size: 15px;
            font-weight: 500;
            line-height: 1.6;
            text-align: center;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # CENTER LAYOUT
    # =====================================================

    left, center, right = st.columns(
        [1, 1.3, 1]
    )

    with center:

        # =================================================
        # COMPANY LOGO
        # =================================================

        logo_container = st.container(
            horizontal_alignment="center"
        )

        with logo_container:

            if os.path.exists(logo_path):

                st.image(
                    logo_path,
                    width=120
                )


        # =================================================
        # COMPANY NAME
        # =================================================

        st.markdown(
            f"""
            <div class="login-brand-title">
                {constants.COMPANY_NAME}
            </div>
            """,
            unsafe_allow_html=True
        )


        # =================================================
        # COMPANY DESCRIPTION
        # =================================================

        st.markdown(
            f"""
            <div class="login-brand-description">
                {constants.DESCRIPTION}
            </div>
            """,
            unsafe_allow_html=True
        )


        # =================================================
        # DIVIDER
        # =================================================

        st.divider()


        # =================================================
        # LOGIN / SIGNUP TABS
        # =================================================

        login_tab, signup_tab = st.tabs(
            [
                "🔐 Login",
                "📝 Sign Up"
            ]
        )


        # =================================================
        # LOGIN
        # =================================================

        with login_tab:

            st.markdown(
                "### Welcome Back"
            )


            with st.form("login_form"):

                username = text_input(
                    "Username",
                    placeholder="Enter your username"
                )


                password = text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password"
                )


                login_clicked = submit_button(
                    "🔐 Login",
                    width="stretch",
                    type="primary"
                )


            # =================================================
            # LOGIN ACTION
            # =================================================

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

                        # -------------------------------------
                        # CREATE STREAMLIT SESSION
                        # -------------------------------------

                        st.session_state["user"] = {
                            "id": user.id,
                            "username": user.username,
                            "role": user.role
                        }


                        # -------------------------------------
                        # CREATE LOGIN SESSION
                        # -------------------------------------

                        token, expires_at = (
                            create_login_session(
                                user_id=user.id
                            )
                        )


                        # -------------------------------------
                        # SAVE TOKEN IN COOKIE
                        # -------------------------------------

                        cookie_manager = (
                            get_cookie_manager()
                        )


                        cookie_manager.set(
                            "security_session",
                            token,
                            expires_at=expires_at
                        )


                        # -------------------------------------
                        # SUCCESS
                        # -------------------------------------

                        st.success(
                            f"Welcome, {user.username}!"
                        )


                        st.rerun()


        # =================================================
        # SIGN UP
        # =================================================

        with signup_tab:

            st.markdown(
                "### Create an Account"
            )


            st.caption(
                "Create an account to access the SecureGuard system."
            )


            with st.form("signup_form"):

                # -----------------------------------------
                # ROLE
                # -----------------------------------------

                new_role = select_box(
                    "Register As",
                    [
                        UserRole.CLIENT.value,
                        UserRole.SECURITY_GUARD.value
                    ]
                )


                # -----------------------------------------
                # USERNAME
                # -----------------------------------------

                new_username = text_input(
                    "Username",
                    placeholder="Choose a username"
                )


                # -----------------------------------------
                # PASSWORD
                # -----------------------------------------

                new_password = text_input(
                    "Password",
                    type="password",
                    placeholder="Create a password"
                )


                # -----------------------------------------
                # CONFIRM PASSWORD
                # -----------------------------------------

                confirm_password = text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Confirm your password"
                )


                # -----------------------------------------
                # SIGNUP BUTTON
                # -----------------------------------------

                signup_clicked = submit_button(
                    "📝 Create Account",
                    width="stretch"
                )


            # =================================================
            # SIGNUP ACTION
            # =================================================

            if signup_clicked:

                # ---------------------------------------------
                # VALIDATION
                # ---------------------------------------------

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

                    # -----------------------------------------
                    # CREATE USER
                    # -----------------------------------------

                    user, error = create_user(
                        username=new_username.strip(),
                        password=new_password,
                        role=new_role
                    )


                    if error:

                        st.error(
                            error
                        )

                    else:

                        st.success(
                            "Account created successfully! "
                            "You can now log in."
                        )