import streamlit as st


def apply_global_styles():

    st.markdown(
        """
        <style>

        /* =========================================================
           GLOBAL THEME
        ========================================================= */

        .stApp {
            background: #0e1624;
            color: #d8e1ef;
        }


        /* =========================================================
           MAIN CONTAINER
        ========================================================= */

        .block-container {
            padding-top: 2rem;
            padding-left: 3rem;
            padding-right: 3rem;
            max-width: 1500px;
        }


        /* =========================================================
           HEADINGS
        ========================================================= */

        h1 {
            color: #f1f4f9 !important;
            font-weight: 700 !important;
        }

        h2, h3 {
            color: #e5eaf2 !important;
        }


        /* =========================================================
           LABELS
        ========================================================= */

        .stTextInput label,
        .stNumberInput label,
        .stSelectbox label,
        .stDateInput label,
        .stTextArea label,
        .stFileUploader label,
        .stCheckbox label {
            color: #aebed2 !important;
            font-size: 0.88rem !important;
            font-weight: 500 !important;
        }


        /* =========================================================
           TEXT INPUT
        ========================================================= */

        .stTextInput input {
            background-color: #1b2638 !important;
            color: #e8edf5 !important;
            border: 1px solid #34445b !important;
            border-radius: 10px !important;
            min-height: 46px !important;
        }

        .stTextInput input:focus {
            border-color: #7754e8 !important;
            box-shadow: 0 0 0 1px #7754e8 !important;
        }


        /* =========================================================
           TEXT AREA
        ========================================================= */

        .stTextArea textarea {
            background-color: #1b2638 !important;
            color: #e8edf5 !important;
            border: 1px solid #34445b !important;
            border-radius: 10px !important;
        }

        .stTextArea textarea:focus {
            border-color: #7754e8 !important;
            box-shadow: 0 0 0 1px #7754e8 !important;
        }


        /* =========================================================
           NUMBER INPUT
        ========================================================= */

        .stNumberInput input {
            background-color: #1b2638 !important;
            color: #e8edf5 !important;
            border: 1px solid #34445b !important;
            border-radius: 10px !important;
            min-height: 46px !important;
        }

        .stNumberInput button {
            background-color: #263246 !important;
            color: #d8e1ef !important;
            border: 1px solid #34445b !important;
        }


        /* =========================================================
           SELECT BOX
        ========================================================= */

        div[data-baseweb="select"] > div {
            background-color: #1b2638 !important;
            border: 1px solid #34445b !important;
            border-radius: 10px !important;
            color: #e8edf5 !important;
            min-height: 46px !important;
        }

        div[data-baseweb="select"] * {
            color: #e8edf5 !important;
        }


        /* =========================================================
           DATE INPUT
        ========================================================= */

        .stDateInput input {
            background-color: #1b2638 !important;
            color: #e8edf5 !important;
            border: 1px solid #34445b !important;
            border-radius: 10px !important;
            min-height: 46px !important;
        }


        /* =========================================================
           PASSWORD EYE BUTTON
        ========================================================= */

        .stTextInput button {
            background-color: #263246 !important;
            border-color: #34445b !important;
            color: #c7d2e3 !important;
        }


        /* =========================================================
           CHECKBOX
        ========================================================= */

        .stCheckbox {
            color: #c7d2e3 !important;
        }


        /* =========================================================
           FILE UPLOADER
        ========================================================= */

        [data-testid="stFileUploader"] {
            background-color: #1b2638 !important;
            border: 1px solid #34445b !important;
            border-radius: 10px !important;
            padding: 8px !important;
        }

        [data-testid="stFileUploader"] section {
            background-color: #1b2638 !important;
            border: none !important;
        }

        [data-testid="stFileUploader"] button {
            background-color: #263246 !important;
            color: #d8e1ef !important;
            border: 1px solid #42536b !important;
            border-radius: 8px !important;
        }


        /* =========================================================
           PRIMARY BUTTON
        ========================================================= */

        .stButton > button {
            width: 100%;
            min-height: 46px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(
                135deg,
                #5c3ccf,
                #8057e8
            );
            color: white;
            font-weight: 600;
            transition: 0.2s;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(112, 76, 220, 0.35);
            border: none;
        }


        /* =========================================================
           DATAFRAME / TABLE
        ========================================================= */

        [data-testid="stDataFrame"] {
            border: 1px solid #34445b;
            border-radius: 10px;
            overflow: hidden;
        }


        /* =========================================================
           EXPANDER
        ========================================================= */

        .streamlit-expanderHeader {
            background-color: #1b2638 !important;
            border-radius: 10px !important;
            color: #e8edf5 !important;
        }


        /* =========================================================
           DIVIDER
        ========================================================= */

        hr {
            border-color: #2b3a50 !important;
        }


        /* =========================================================
           SUCCESS MESSAGE
        ========================================================= */

        .stSuccess {
            background-color: #14382d !important;
            color: #c5f6dd !important;
            border: 1px solid #246b4f !important;
            border-radius: 10px !important;
        }


        /* =========================================================
           ERROR MESSAGE
        ========================================================= */

        .stError {
            background-color: #3b2026 !important;
            color: #ffb4bd !important;
            border: 1px solid #743640 !important;
            border-radius: 10px !important;
        }


        /* =========================================================
           INFO MESSAGE
        ========================================================= */

        .stInfo {
            background-color: #1d3047 !important;
            color: #b7d8ff !important;
            border: 1px solid #365b7c !important;
            border-radius: 10px !important;
        }


        /* =========================================================
           METRIC CARDS
        ========================================================= */

        [data-testid="stMetric"] {
            background-color: #172235;
            border: 1px solid #2d3d54;
            border-radius: 16px;
            padding: 20px;
        }


        /* =========================================================
           TABS
        ========================================================= */

        button[data-baseweb="tab"] {
            color: #9eafc4 !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #e9e1ff !important;
        }

        [data-baseweb="tab-highlight"] {
            background-color: #7855e8 !important;
        }


        /* =========================================================
           FORM CONTAINER
        ========================================================= */

        [data-testid="stForm"] {
            background-color: #111a29;
            border: 1px solid #202d40;
            border-radius: 14px;
            padding: 20px;
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

        </style>
        """,
        unsafe_allow_html=True
    )