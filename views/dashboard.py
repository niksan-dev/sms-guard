import streamlit as st


def show_dashboard():

    user = st.session_state["user"]

    st.markdown(
        f"""
        # Dashboard

        Welcome back, **{user['username']}** 👋

        You are logged in as **{user['role']}**.
        """
    )

    st.divider()

    # Dashboard Metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "👮 Total Guards",
        "0"
    )

    col2.metric(
        "🟢 Present Today",
        "0"
    )

    col3.metric(
        "🔴 Absent Today",
        "0"
    )

    col4.metric(
        "🏢 Active Sites",
        "0"
    )

    col5.metric(
        "⚠️ Open Incidents",
        "0"
    )

    st.divider()

    left_col, right_col = st.columns([2, 1])

    with left_col:

        st.subheader("📅 Today's Shifts")

        st.info(
            "No shifts available yet."
        )

    with right_col:

        st.subheader("⚠️ Recent Incidents")

        st.info(
            "No incidents available yet."
        )