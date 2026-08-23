import streamlit as st


def load_custom_css():
    st.markdown("""
    <style>

    /* =========================================================
       GLOBAL VARIABLES
    ========================================================= */

    :root {
        --primary: #6D42D8;
        --primary-light: #8B6CF0;
        --primary-dark: #5130B5;

        --bg-main: #0F1724;
        --bg-sidebar: #131E2E;
        --bg-card: #1C293B;
        --bg-input: #202C3D;

        --border: #314158;
        --border-light: #40516A;

        --text-main: #F3F6FB;
        --text-secondary: #A9B7CA;
        --text-muted: #78879A;

        --success: #41C987;
        --warning: #F5A524;
        --danger: #FF5C63;
    }


    /* =========================================================
       APP BACKGROUND
    ========================================================= */

    .stApp {
        background-color: var(--bg-main);
        color: var(--text-main);
    }

    [data-testid="stAppViewContainer"] {
        background-color: var(--bg-main);
    }

    [data-testid="stMain"] {
        background-color: var(--bg-main);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1600px;
    }


    /* =========================================================
       TEXT
    ========================================================= */

    h1, h2, h3, h4, h5, h6 {
        color: var(--text-main) !important;
        font-weight: 700 !important;
    }

    p, span, label {
        color: inherit;
    }

    .stMarkdown {
        color: var(--text-main);
    }


    /* =========================================================
       DIVIDERS
    ========================================================= */

    hr {
        border-color: var(--border) !important;
    }


    /* =========================================================
       FORM INPUTS
    ========================================================= */

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input,
    [data-testid="stTimeInput"] input,
    [data-testid="stTextArea"] textarea {
        background-color: var(--bg-input) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        min-height: 42px;
    }

    [data-testid="stTextArea"] textarea {
        min-height: 110px;
    }

    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stDateInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--primary-light) !important;
        box-shadow: 0 0 0 2px rgba(109, 66, 216, 0.18) !important;
    }

    [data-testid="stTextInput"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stDateInput"] label,
    [data-testid="stSelectbox"] label,
    [data-testid="stTextArea"] label {
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
    }


    /* =========================================================
       SELECT BOX
    ========================================================= */

    [data-testid="stSelectbox"] > div > div {
        background-color: var(--bg-input) !important;
        border-color: var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-main) !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] {
        background-color: var(--bg-input) !important;
    }

    [data-baseweb="select"] * {
        color: var(--text-main);
    }


    /* =========================================================
       DATE INPUT
    ========================================================= */

    [data-testid="stDateInput"] > div {
        background-color: var(--bg-input) !important;
        border-radius: 10px !important;
    }


    /* =========================================================
       CHECKBOX
    ========================================================= */

    [data-testid="stCheckbox"] {
        color: var(--text-secondary) !important;
    }


    /* =========================================================
       BUTTONS
    ========================================================= */

    .stButton > button {
        min-height: 42px;
        border-radius: 10px;
        border: 1px solid var(--border);
        background-color: var(--bg-card);
        color: var(--text-main);
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: var(--primary-light);
        color: white;
        transform: translateY(-1px);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(
            135deg,
            var(--primary),
            var(--primary-light)
        ) !important;

        border-color: var(--primary-light) !important;
        color: white !important;
    }

    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 8px 20px rgba(109, 66, 216, 0.30);
    }


    /* =========================================================
       FORMS
    ========================================================= */

    [data-testid="stForm"] {
        background-color: transparent !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        padding: 1.25rem !important;
    }


    /* =========================================================
       EXPANDER
    ========================================================= */

    [data-testid="stExpander"] {
        background-color: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }


    /* =========================================================
       DATAFRAMES
    ========================================================= */

    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
        background-color: var(--bg-card);
    }


    /* =========================================================
       TABLES
    ========================================================= */

    .stTable {
        border: 1px solid var(--border);
        border-radius: 10px;
        overflow: hidden;
    }

    .stTable table {
        color: var(--text-main);
        background-color: var(--bg-card);
    }


    /* =========================================================
       METRIC CARDS
    ========================================================= */

    [data-testid="stMetric"] {
        background-color: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.25rem;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--text-main) !important;
        font-weight: 700 !important;
    }


    /* =========================================================
       ALERTS
    ========================================================= */

    [data-testid="stAlert"] {
        border-radius: 10px;
        border: 1px solid var(--border);
    }


    /* =========================================================
       FILE UPLOADER
    ========================================================= */

    [data-testid="stFileUploader"] {
        background-color: var(--bg-card);
        border-radius: 12px;
    }


    /* =========================================================
       TABS
    ========================================================= */

    [data-testid="stTabs"] button {
        color: var(--text-secondary) !important;
        font-weight: 600;
    }

    [data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--text-main) !important;
    }


    /* =========================================================
       SIDEBAR BASE
    ========================================================= */

    [data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border) !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background-color: var(--bg-sidebar) !important;
    }


    /* =========================================================
       SCROLLBAR
    ========================================================= */

    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-thumb {
        background-color: #334155;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-track {
        background-color: transparent;
    }


    /* =========================================================
       HIDE STREAMLIT DEFAULT ELEMENTS
    ========================================================= */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    [data-testid="stToolbar"] {
        visibility: hidden;
    }

    </style>
    """, unsafe_allow_html=True)