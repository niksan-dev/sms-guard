import streamlit as st
import extra_streamlit_components as stx


def get_cookie_manager():

    if "cookie_manager" not in st.session_state:

        st.session_state["cookie_manager"] = (
            stx.CookieManager(
                key="secureguard_cookie_manager"
            )
        )

    return st.session_state["cookie_manager"]

