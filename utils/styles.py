import streamlit as st


def load_custom_css():

    st.markdown("""
    <style>

    /* =====================================================
       IMPORT FONT
    ===================================================== */

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');


    /* =====================================================
       GLOBAL
    ===================================================== */

    html,
    body,
    [class*="css"] {

        font-family: 'Inter', sans-serif;
    }


    /* =====================================================
       MAIN APP BACKGROUND
    ===================================================== */

    .stApp {

        background:
            radial-gradient(
                circle at top right,
                rgba(80, 70, 160, 0.12),
                transparent 30%
            ),
            #0B101A;

        color: #E8EDF7;
    }


    /* =====================================================
       MAIN CONTENT
    ===================================================== */

    .main .block-container {

        padding-top: 2.5rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1500px;
    }


    /* =====================================================
       SIDEBAR
    ===================================================== */

    section[data-testid="stSidebar"] {

        background:
            linear-gradient(
                180deg,
                #111A2B 0%,
                #0B1220 100%
            );

        border-right:
            1px solid #263247;

        min-width: 300px;
    }


    section[data-testid="stSidebar"] > div {

        padding-top: 1rem;
    }


    /* =====================================================
       HEADINGS
    ===================================================== */

    h1 {

        color: #F4F6FB !important;

        font-weight: 800 !important;

        letter-spacing: -1px;

        font-size: 2.6rem !important;
    }


    h2 {

        color: #E8EDF7 !important;

        font-weight: 700 !important;
    }


    h3 {

        color: #E8EDF7 !important;

        font-weight: 600 !important;
    }


    p,
    label {

        color: #B8C1D1 !important;
    }


    /* =====================================================
       DIVIDER
    ===================================================== */

    hr {

        border-color: #273247 !important;
    }


    /* =====================================================
       BUTTONS
    ===================================================== */

    .stButton > button {

        width: 100%;

        background:
            linear-gradient(
                135deg,
                #6941C6,
                #8B5CF6
            );

        color: white;

        border: none;

        border-radius: 10px;

        font-weight: 600;

        min-height: 44px;

        transition:
            all 0.2s ease;
    }


    .stButton > button:hover {

        transform:
            translateY(-2px);

        box-shadow:
            0 8px 25px
            rgba(124, 58, 237, 0.35);
    }


    /* =====================================================
       INPUTS
    ===================================================== */

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {

        background-color: #161F2E !important;

        color: #F4F6FB !important;

        border:
            1px solid #2B374C !important;

        border-radius: 10px !important;
    }


    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stNumberInput input:focus {

        border:
            1px solid #7C5CFC !important;

        box-shadow:
            0 0 0 2px
            rgba(124, 92, 252, 0.15) !important;
    }


    /* =====================================================
       SELECT BOX
    ===================================================== */

    div[data-baseweb="select"] > div {

        background-color: #161F2E !important;

        border:
            1px solid #2B374C !important;

        border-radius: 10px !important;
    }


    /* =====================================================
       METRIC CARDS
    ===================================================== */

    div[data-testid="stMetric"] {

        background:
            linear-gradient(
                145deg,
                #161F2E,
                #111827
            );

        padding: 22px;

        border-radius: 16px;

        border:
            1px solid #273247;

        box-shadow:
            0 10px 30px
            rgba(0, 0, 0, 0.15);
    }


    div[data-testid="stMetricLabel"] {

        color: #98A2B3 !important;
    }


    div[data-testid="stMetricValue"] {

        color: #F4F6FB !important;

        font-weight: 700;
    }


    /* =====================================================
       DATAFRAME
    ===================================================== */

    div[data-testid="stDataFrame"] {

        border-radius: 12px;

        overflow: hidden;

        border:
            1px solid #273247;
    }


    /* =====================================================
       TABS
    ===================================================== */

    button[data-baseweb="tab"] {

        color: #98A2B3;

        font-weight: 600;
    }


    button[data-baseweb="tab"][aria-selected="true"] {

        color: #A78BFA;

        border-bottom:
            2px solid #8B5CF6 !important;
    }


    /* =====================================================
       EXPANDER
    ===================================================== */

    div[data-testid="stExpander"] {

        background: #111827;

        border:
            1px solid #273247;

        border-radius: 12px;
    }


    /* =====================================================
       ALERTS
    ===================================================== */

    div[data-testid="stAlert"] {

        border-radius: 12px;
    }


    /* =====================================================
       HIDE STREAMLIT DEFAULT ELEMENTS
    ===================================================== */

    #MainMenu {

        visibility: hidden;
    }


    footer {

        visibility: hidden;
    }


    header {

        background: transparent !important;
    }


    /* =====================================================
    SIDEBAR RADIO NAVIGATION
    ===================================================== */

    section[data-testid="stSidebar"]
    div[role="radiogroup"] {

        gap: 10px;
    }


    section[data-testid="stSidebar"]
    label[data-baseweb="radio"] {

        background: #172235;

        border: 1px solid #263247;

        border-radius: 14px;

        padding: 15px;

        min-height: 58px;

        transition:
            all 0.2s ease;
    }


    section[data-testid="stSidebar"]
    label[data-baseweb="radio"]:hover {

        background: #202C40;

        transform:
            translateX(3px);
    }



    /* ==========================================
        SIDEBAR NAVIGATION
        ========================================== */

        section[data-testid="stSidebar"] div[role="radiogroup"] {
            gap: 10px;
        }


        /* Navigation item */

        section[data-testid="stSidebar"] div[role="radiogroup"] label {
            background: #1E293B;
            border: 1px solid #2D3748;

            border-radius: 14px;

            padding: 14px 16px;

            min-height: 58px;

            transition:
                all 0.25s ease;

            cursor: pointer;
        }


        /* Hide default radio circle */

        section[data-testid="stSidebar"] div[role="radiogroup"] label input {
            display: none;
        }


        /* Text */

        section[data-testid="stSidebar"] div[role="radiogroup"] label p {
            font-size: 16px;
            font-weight: 600;

            color: #CBD5E1;
        }


        /* Hover */

        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background: #273449;

            border-color: #4F46E5;

            transform: translateX(4px);
        }


        /* ==========================================
        ACTIVE NAVIGATION TAB
        ========================================== */

        section[data-testid="stSidebar"]
        div[role="radiogroup"]
        label:has(input:checked) {

            background: linear-gradient(
                135deg,
                #4F46E5,
                #7C3AED
            );

            border-color: #8B5CF6;

            box-shadow:
                0 6px 20px
                rgba(124, 58, 237, 0.35);
        }


        /* Active text */

        section[data-testid="stSidebar"]
        div[role="radiogroup"]
        label:has(input:checked) p {

            color: white;

            font-weight: 700;
        }


        /* ==================================================
        PREMIUM DASHBOARD CARDS
        ================================================== */

        .dashboard-card {
            background: linear-gradient(145deg, #1e293b, #111827);
            border: 1px solid #334155;
            border-radius: 18px;
            padding: 22px;
            min-height: 150px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
            transition: all 0.25s ease;
        }

        .dashboard-card:hover {
            transform: translateY(-5px);
            border-color: #7c3aed;
            box-shadow: 0 12px 30px rgba(124, 58, 237, 0.22);
        }

        .dashboard-card-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .dashboard-card-title {
            color: #94a3b8;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.8px;
            text-transform: uppercase;
        }

        .dashboard-card-icon {
            width: 45px;
            height: 45px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 23px;
        }

        .icon-purple {
            background: rgba(124, 58, 237, 0.18);
        }

        .icon-green {
            background: rgba(34, 197, 94, 0.18);
        }

        .icon-blue {
            background: rgba(59, 130, 246, 0.18);
        }

        .icon-red {
            background: rgba(239, 68, 68, 0.18);
        }

        .icon-orange {
            background: rgba(249, 115, 22, 0.18);
        }

        .icon-cyan {
            background: rgba(6, 182, 212, 0.18);
        }

        .dashboard-card-value {
            color: #f8fafc;
            font-size: 36px;
            font-weight: 800;
            margin-top: 20px;
            line-height: 1;
        }

        .dashboard-card-footer {
            color: #94a3b8;
            font-size: 13px;
            margin-top: 12px;
        }

        .status-positive {
            color: #22c55e;
            font-weight: 700;
        }

        .status-warning {
            color: #f59e0b;
            font-weight: 700;
        }

        .status-danger {
            color: #ef4444;
            font-weight: 700;
        }

    </style>
    """, unsafe_allow_html=True)


