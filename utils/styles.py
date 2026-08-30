import streamlit as st


def load_custom_css():

    st.markdown(
        """
        <style>

        /* =========================================================
           AADHAR SECURITY SERVICES
           PROFESSIONAL LIGHT THEME
        ========================================================= */

        :root {
            --primary: #063552;
            --primary-dark: #04283E;
            --primary-light: #EAF3F8;

            --secondary: #69DA25;
            --secondary-dark: #55B91B;
            --secondary-light: #F0FBE9;

            --page-bg: #F5F7FA;
            --card-bg: #FFFFFF;

            --text: #17202A;
            --text-secondary: #667085;
            --text-muted: #98A2B3;

            --border: #E4E7EC;
            --border-dark: #D0D5DD;

            --success: #16A34A;
            --warning: #D97706;
            --danger: #DC2626;

            --shadow-sm:
                0 1px 3px rgba(16, 24, 40, 0.08);

            --shadow-md:
                0 4px 12px rgba(16, 24, 40, 0.08);

            --shadow-lg:
                0 10px 30px rgba(16, 24, 40, 0.10);

            --radius: 10px;
        }


        /* =========================================================
           APP BACKGROUND
        ========================================================= */

        .stApp,
        .stApp > div,
        [data-testid="stAppViewContainer"] {

            background: var(--page-bg) !important;

            color: var(--text) !important;
        }


        [data-testid="stAppViewContainer"] > section {

            background: var(--page-bg) !important;
        }


        [data-testid="stMain"] {

            background: var(--page-bg) !important;
        }


        [data-testid="stMainBlockContainer"] {

            background: transparent !important;

            padding-top: 2rem !important;

            padding-bottom: 3rem !important;

            max-width: 1500px !important;
        }


        .main .block-container {

            background: transparent !important;

            padding-top: 2rem !important;

            padding-left: 2.5rem !important;

            padding-right: 2.5rem !important;

            padding-bottom: 3rem !important;

            max-width: 1500px !important;
        }


        /* =========================================================
           GLOBAL TEXT
        ========================================================= */

        html,
        body {

            background: var(--page-bg) !important;

            color: var(--text) !important;
        }


        p,
        span,
        div {

            color: inherit;
        }


        h1,
        h2,
        h3,
        h4,
        h5,
        h6 {

            color: var(--text) !important;
        }


        h1 {

            font-size: 2.2rem !important;

            font-weight: 800 !important;

            letter-spacing: -0.5px !important;
        }


        h2 {

            font-size: 1.7rem !important;

            font-weight: 750 !important;
        }


        h3 {

            font-size: 1.35rem !important;

            font-weight: 700 !important;
        }


        /* =========================================================
           SIDEBAR
        ========================================================= */

        section[data-testid="stSidebar"] {

            background: #FFFFFF !important;

            border-right:
                1px solid var(--border) !important;

            box-shadow:
                2px 0 10px rgba(16, 24, 40, 0.04);
        }


        section[data-testid="stSidebar"] > div {

            background: #FFFFFF !important;
        }


        section[data-testid="stSidebar"] * {

            color: var(--text) !important;
        }


        /* Sidebar headings */

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {

            color: var(--primary) !important;
        }


        /* =========================================================
           SIDEBAR RADIO / MENU
        ========================================================= */

        section[data-testid="stSidebar"]
        div[role="radiogroup"] {

            gap: 6px !important;
        }


        section[data-testid="stSidebar"]
        div[role="radiogroup"]
        label {

            display: flex !important;

            align-items: center !important;

            background: #FFFFFF !important;

            border:
                1px solid transparent !important;

            border-radius: 9px !important;

            padding: 11px 13px !important;

            margin: 2px 0 !important;

            min-height: 46px !important;

            transition:
                background 0.15s ease,
                border 0.15s ease,
                transform 0.15s ease !important;
        }


        section[data-testid="stSidebar"]
        div[role="radiogroup"]
        label:hover {

            background:
                var(--primary-light) !important;

            border-color:
                #D7E7F0 !important;

            transform:
                translateX(2px) !important;
        }


        section[data-testid="stSidebar"]
        div[role="radiogroup"]
        label p {

            color:
                #344054 !important;

            font-size:
                14px !important;

            font-weight:
                600 !important;
        }


        /* ACTIVE SIDEBAR ITEM */

        section[data-testid="stSidebar"]
        div[role="radiogroup"]
        label:has(input:checked) {

            background:
                var(--primary) !important;

            border-color:
                var(--primary) !important;

            box-shadow:
                0 3px 10px
                rgba(6, 53, 82, 0.18) !important;
        }


        section[data-testid="stSidebar"]
        div[role="radiogroup"]
        label:has(input:checked) p {

            color:
                #FFFFFF !important;

            font-weight:
                700 !important;
        }


        /* =========================================================
           BUTTONS
        ========================================================= */

        .stButton > button,
        .stFormSubmitButton > button {

            min-height: 42px !important;

            border-radius: 8px !important;

            font-weight: 600 !important;

            font-size: 14px !important;

            transition:
                all 0.15s ease !important;
        }


        /* PRIMARY BUTTON */

        .stButton > button[kind="primary"],
        .stFormSubmitButton > button[kind="primary"] {

            background:
                var(--primary) !important;

            color:
                #FFFFFF !important;

            border:
                1px solid var(--primary) !important;

            box-shadow:
                0 2px 6px
                rgba(6, 53, 82, 0.15) !important;
        }


        .stButton > button[kind="primary"]:hover,
        .stFormSubmitButton > button[kind="primary"]:hover {

            background:
                var(--primary-dark) !important;

            border-color:
                var(--primary-dark) !important;

            transform:
                translateY(-1px) !important;

            box-shadow:
                0 5px 12px
                rgba(6, 53, 82, 0.20) !important;
        }


        /* SECONDARY BUTTON */

        .stButton > button[kind="secondary"],
        .stFormSubmitButton > button[kind="secondary"] {

            background:
                #FFFFFF !important;

            color:
                var(--primary) !important;

            border:
                1px solid var(--border-dark) !important;

            box-shadow:
                var(--shadow-sm) !important;
        }


        .stButton > button[kind="secondary"]:hover,
        .stFormSubmitButton > button[kind="secondary"]:hover {

            background:
                var(--primary-light) !important;

            color:
                var(--primary-dark) !important;

            border-color:
                #9DBBCC !important;
        }


        /* =========================================================
           GREEN ACTION BUTTON
        ========================================================= */

        .aadhar-green-button {

            background:
                var(--secondary) !important;

            color:
                #063552 !important;

            border:
                none !important;

            border-radius:
                8px !important;

            font-weight:
                700 !important;

            padding:
                10px 18px !important;

            cursor:
                pointer !important;
        }


        .aadhar-green-button:hover {

            background:
                var(--secondary-dark) !important;
        }


        /* =========================================================
        INPUT BOXES — STRONGER BORDER + SHADOW
        ========================================================= */

        .stTextInput > div > div,
        .stTextArea > div > div,
        .stNumberInput > div > div,
        .stDateInput > div > div,
        .stTimeInput > div > div {

            background: #FFFFFF !important;

            border: 1px solid #B8C2CC !important;

            border-radius: 9px !important;

            box-shadow:
                0 1px 3px rgba(6, 53, 82, 0.10),
                0 1px 2px rgba(0, 0, 0, 0.04) !important;

            transition:
                border-color 0.15s ease,
                box-shadow 0.15s ease !important;
        }


        /* Actual input */

        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input,
        .stDateInput input,
        .stTimeInput input {

            background: #FFFFFF !important;

            color: #17202A !important;

            border: none !important;

            outline: none !important;

            box-shadow: none !important;
        }


        /* Hover */

        .stTextInput > div > div:hover,
        .stTextArea > div > div:hover,
        .stNumberInput > div > div:hover,
        .stDateInput > div > div:hover,
        .stTimeInput > div > div:hover {

            border-color: #063552 !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.12) !important;
        }


        /* Focus */

        .stTextInput > div > div:focus-within,
        .stTextArea > div > div:focus-within,
        .stNumberInput > div > div:focus-within,
        .stDateInput > div > div:focus-within,
        .stTimeInput > div > div:focus-within {

            border-color: #063552 !important;

            box-shadow:
                0 0 0 3px rgba(6, 53, 82, 0.10),
                0 2px 6px rgba(6, 53, 82, 0.12) !important;
        }


        /* =========================================================
           INPUT LABELS
        ========================================================= */

        .stTextInput label,
        .stTextArea label,
        .stNumberInput label,
        .stSelectbox label,
        .stMultiSelect label,
        .stDateInput label,
        .stTimeInput label,
        .stFileUploader label,
        .stCheckbox label {

            color:
                #344054 !important;

            font-size:
                13px !important;

            font-weight:
                600 !important;
        }


        /* =========================================================
           SELECTBOX
        ========================================================= */

        div[data-baseweb="select"] > div {

            background:
                #FFFFFF !important;

            border:
                1px solid var(--border-dark) !important;

            border-radius:
                8px !important;

            min-height:
                42px !important;
        }


        div[data-baseweb="select"] span {

            color:
                #17202A !important;
        }


        div[data-baseweb="select"] > div:hover {

            border-color:
                #98A2B3 !important;
        }


        /* Dropdown menu */

        div[data-baseweb="popover"] {

            background:
                #FFFFFF !important;

            border:
                1px solid var(--border) !important;

            box-shadow:
                var(--shadow-lg) !important;
        }


        div[data-baseweb="menu"] {

            background:
                #FFFFFF !important;
        }


        div[data-baseweb="menu"] li {

            color:
                #17202A !important;

            background:
                #FFFFFF !important;
        }


        div[data-baseweb="menu"] li:hover {

            background:
                var(--primary-light) !important;
        }


        /* =========================================================
           MULTISELECT
        ========================================================= */

        div[data-baseweb="select"]
        div[role="option"] {

            background:
                #FFFFFF !important;

            color:
                #17202A !important;
        }


        /* =========================================================
           CHECKBOX
        ========================================================= */

        .stCheckbox label {

            color:
                #344054 !important;
        }


        /* =========================================================
           FILE UPLOADER
        ========================================================= */

        div[data-testid="stFileUploader"] {

            background:
                #FFFFFF !important;

            border:
                1px solid var(--border) !important;

            border-radius:
                10px !important;

            padding:
                8px !important;

            box-shadow:
                var(--shadow-sm) !important;
        }


        div[data-testid="stFileUploaderDropzone"] {

            background:
                #F8FAFC !important;

            border:
                1px dashed #CBD5E1 !important;

            border-radius:
                8px !important;
        }


        div[data-testid="stFileUploaderDropzone"]:hover {

            background:
                var(--primary-light) !important;

            border-color:
                #7C9FB4 !important;
        }


        /* =========================================================
        FORMS
        ========================================================= */

        div[data-testid="stForm"] {

            background: #FFFFFF !important;

            border: 1px solid #D0D5DD !important;

            border-radius: 12px !important;

            padding: 22px !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08) !important;
        }


        /* =========================================================
        FORM HEADER / TITLE
        ========================================================= */

        div[data-testid="stForm"] h1,
        div[data-testid="stForm"] h2,
        div[data-testid="stForm"] h3,
        div[data-testid="stForm"] h4 {

            background: #E8EEF2 !important;

            color: #063552 !important;

            font-weight: 700 !important;

            padding: 11px 14px !important;

            margin-top: -8px !important;

            margin-bottom: 18px !important;

            border-radius: 8px !important;

            border-left: 4px solid #69DA25 !important;
        }


        /* Form header text */

        div[data-testid="stForm"] h1 *,
        div[data-testid="stForm"] h2 *,
        div[data-testid="stForm"] h3 *,
        div[data-testid="stForm"] h4 * {

            color: #063552 !important;

            font-weight: 700 !important;
        }


        /* =========================================================
           METRICS
        ========================================================= */

        div[data-testid="stMetric"] {

            background:
                #FFFFFF !important;

            border:
                1px solid var(--border) !important;

            border-radius:
                12px !important;

            padding:
                18px !important;

            box-shadow:
                var(--shadow-sm) !important;

            transition:
                all 0.2s ease !important;
        }


        div[data-testid="stMetric"]:hover {

            transform:
                translateY(-2px) !important;

            box-shadow:
                var(--shadow-md) !important;

            border-color:
                #C8D9E3 !important;
        }


        div[data-testid="stMetricLabel"] {

            color:
                var(--text-secondary) !important;
        }


        div[data-testid="stMetricValue"] {

            color:
                var(--primary) !important;

            font-weight:
                800 !important;
        }


        /* =========================================================
        DATAFRAME
        AADHAR SECURITY SERVICES
        ========================================================= */

        div[data-testid="stDataFrame"] {

            background: #FFFFFF !important;

            border: 1px solid #C8D1D9 !important;

            border-radius: 10px !important;

            overflow: hidden !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08) !important;

            margin-top: 8px !important;
        }


        /* Dataframe inner container */

        div[data-testid="stDataFrame"] > div {

            background: #FFFFFF !important;
        }


        /* =========================================================
        DATA EDITOR
        ========================================================= */

        div[data-testid="stDataEditor"] {

            background: #FFFFFF !important;

            border: 1px solid #C8D1D9 !important;

            border-radius: 10px !important;

            overflow: hidden !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08) !important;
        }


        /* =========================================================
        NORMAL HTML TABLE
        Used if st.table() is used anywhere
        ========================================================= */

        .stTable {

            width: 100% !important;

            background: #FFFFFF !important;

            border: 1px solid #C8D1D9 !important;

            border-radius: 10px !important;

            overflow: hidden !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08) !important;
        }


        .stTable table {

            width: 100% !important;

            border-collapse: collapse !important;

            background: #FFFFFF !important;
        }


        /* Table header */

        .stTable th {

            background: #E1E8ED !important;

            color: #063552 !important;

            font-weight: 700 !important;

            font-size: 13px !important;

            text-align: left !important;

            padding: 10px 12px !important;

            border: 1px solid #C8D1D9 !important;
        }


        /* Table body */

        .stTable td {

            background: #FFFFFF !important;

            color: #17202A !important;

            font-size: 13px !important;

            padding: 9px 12px !important;

            border: 1px solid #E1E5E9 !important;
        }


        /* Row hover */

        .stTable tbody tr:hover td {

            background: #F4F8FA !important;
        }


        /* =========================================================
           TABS
        ========================================================= */

        button[data-baseweb="tab"] {

            color:
                #667085 !important;

            font-weight:
                600 !important;

            background:
                transparent !important;
        }


        button[data-baseweb="tab"]:hover {

            color:
                var(--primary) !important;
        }


        button[data-baseweb="tab"][aria-selected="true"] {

            color:
                var(--primary) !important;
        }


        [data-baseweb="tab-highlight"] {

            background:
                var(--secondary) !important;
        }


        /* =========================================================
           EXPANDER
        ========================================================= */

        div[data-testid="stExpander"] {

            background:
                #FFFFFF !important;

            border:
                1px solid var(--border) !important;

            border-radius:
                10px !important;

            box-shadow:
                var(--shadow-sm) !important;
        }


        div[data-testid="stExpander"] summary {

            background:
                #FFFFFF !important;

            color:
                #344054 !important;
        }


        /* =========================================================
           ALERTS
        ========================================================= */

        div[data-testid="stAlert"] {

            border-radius:
                8px !important;
        }


        /* =========================================================
           SUCCESS
        ========================================================= */

        .stSuccess {

            background:
                #F0FDF4 !important;

            color:
                #166534 !important;

            border:
                1px solid #BBF7D0 !important;
        }


        /* =========================================================
           ERROR
        ========================================================= */

        .stError {

            background:
                #FEF2F2 !important;

            color:
                #991B1B !important;

            border:
                1px solid #FECACA !important;
        }


        /* =========================================================
           WARNING
        ========================================================= */

        .stWarning {

            background:
                #FFFBEB !important;

            color:
                #92400E !important;

            border:
                1px solid #FDE68A !important;
        }


        /* =========================================================
           INFO
        ========================================================= */

        .stInfo {

            background:
                var(--primary-light) !important;

            color:
                var(--primary) !important;

            border:
                1px solid #C7DCE8 !important;
        }


        /* =========================================================
           DASHBOARD CARD
        ========================================================= */

        .dashboard-card {

            background:
                #FFFFFF !important;

            border:
                1px solid var(--border) !important;

            border-radius:
                14px !important;

            padding:
                20px !important;

            box-shadow:
                var(--shadow-sm) !important;

            transition:
                all 0.2s ease !important;
        }


        .dashboard-card:hover {

            transform:
                translateY(-3px) !important;

            box-shadow:
                var(--shadow-md) !important;

            border-color:
                #C8D9E3 !important;
        }


        .dashboard-card-title {

            color:
                var(--text-secondary) !important;

            font-size:
                12px !important;

            font-weight:
                700 !important;

            text-transform:
                uppercase !important;

            letter-spacing:
                0.5px !important;
        }


        .dashboard-card-value {

            color:
                var(--primary) !important;

            font-size:
                32px !important;

            font-weight:
                800 !important;
        }


        .dashboard-card-footer {

            color:
                var(--text-secondary) !important;

            font-size:
                13px !important;
        }


        /* =========================================================
           DASHBOARD ICONS
        ========================================================= */

        .dashboard-card-icon {

            width:
                44px;

            height:
                44px;

            border-radius:
                10px;

            display:
                flex;

            align-items:
                center;

            justify-content:
                center;

            font-size:
                21px;
        }


        .icon-blue {

            background:
                var(--primary-light) !important;
        }


        .icon-green {

            background:
                var(--secondary-light) !important;
        }


        .icon-purple {

            background:
                #F4F3FF !important;
        }


        .icon-red {

            background:
                #FEF3F2 !important;
        }


        .icon-orange {

            background:
                #FFF6ED !important;
        }


        .icon-cyan {

            background:
                #ECFDFF !important;
        }


        /* =========================================================
           STATUS
        ========================================================= */

        .status-positive {

            color:
                var(--success) !important;

            font-weight:
                700 !important;
        }


        .status-warning {

            color:
                var(--warning) !important;

            font-weight:
                700 !important;
        }


        .status-danger {

            color:
                var(--danger) !important;

            font-weight:
                700 !important;
        }


        /* =========================================================
           CHART CARD
        ========================================================= */

        .chart-card {

            background:
                #FFFFFF !important;

            border:
                1px solid var(--border) !important;

            border-radius:
                14px !important;

            padding:
                20px !important;

            box-shadow:
                var(--shadow-sm) !important;
        }


        /* =========================================================
           SECTION TITLE
        ========================================================= */

        .dashboard-section-title {

            color:
                var(--primary) !important;

            font-size:
                21px !important;

            font-weight:
                750 !important;

            margin-top:
                20px !important;

            margin-bottom:
                15px !important;
        }


        /* =========================================================
           SPINNER
        ========================================================= */

        .stSpinner > div {

            border-top-color:
                var(--primary) !important;
        }


        /* =========================================================
           LINKS
        ========================================================= */

        a {

            color:
                var(--primary) !important;
        }


        a:hover {

            color:
                var(--secondary-dark) !important;
        }


        /* =========================================================
           SCROLLBAR
        ========================================================= */

        ::-webkit-scrollbar {

            width:
                7px;

            height:
                7px;
        }


        ::-webkit-scrollbar-track {

            background:
                #F1F3F5;
        }


        ::-webkit-scrollbar-thumb {

            background:
                #C5CDD5;

            border-radius:
                10px;
        }


        ::-webkit-scrollbar-thumb:hover {

            background:
                #98A2B3;
        }


        /* =========================================================
           STREAMLIT HEADER
        ========================================================= */

        header[data-testid="stHeader"] {

            background:
                #FFFFFF !important;

            border-bottom:
                1px solid var(--border) !important;
        }


        /* =========================================================
           HIDE DEFAULT STREAMLIT MENU
        ========================================================= */

        #MainMenu {

            visibility:
                hidden;
        }


        footer {

            visibility:
                hidden;
        }


        /* =========================================================
           REMOVE DARK BACKGROUNDS FROM COMMON CONTAINERS
        ========================================================= */

        div[data-testid="stVerticalBlock"],
        div[data-testid="stHorizontalBlock"] {

            color:
                var(--text);
        }


        /* =========================================================
           MOBILE
        ========================================================= */

        @media (max-width: 768px) {

            .main .block-container {

                padding-left:
                    1rem !important;

                padding-right:
                    1rem !important;

                padding-top:
                    1rem !important;
            }


            h1 {

                font-size:
                    1.7rem !important;
            }


            h2 {

                font-size:
                    1.4rem !important;
            }


            .dashboard-card {

                padding:
                    16px !important;
            }

        }



        /* =========================================================
        DASHBOARD
        COMPANY SETTINGS DESIGN LANGUAGE
        ========================================================= */


        /* =========================================================
        DASHBOARD HEADER
        ========================================================= */

        .dashboard-page-title {

            color: #063552;

            font-size: 30px;

            font-weight: 800;

            line-height: 1.2;

            margin-bottom: 4px;
        }


        .dashboard-page-subtitle {

            color: #667085;

            font-size: 14px;

            margin-bottom: 20px;
        }


        /* =========================================================
        DASHBOARD SECTION HEADER
        ========================================================= */

        .dashboard-section-title {

            background: #E1E8ED;

            color: #063552;

            font-size: 18px;

            font-weight: 800;

            padding: 9px 14px;

            border-radius: 8px;

            border-left: 4px solid #69DA25;

            margin-top: 18px;

            margin-bottom: 14px;

            line-height: 1.4;
        }


        /* =========================================================
        PRIMARY DASHBOARD CARDS
        ========================================================= */

        .dashboard-card {

            background: #FFFFFF;

            border: 1px solid #D0D7DE;

            border-radius: 12px;

            padding: 17px 18px;

            min-height: 125px;

            box-sizing: border-box;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.07);

            transition:
                box-shadow 0.15s ease,
                transform 0.15s ease,
                border-color 0.15s ease;
        }


        .dashboard-card:hover {

            border-color: #B8C8D2;

            box-shadow:
                0 4px 12px rgba(6, 53, 82, 0.11);

            transform:
                translateY(-1px);
        }


        /* =========================================================
        CARD TOP
        ========================================================= */

        .dashboard-card-top {

            display: flex;

            align-items: center;

            justify-content: space-between;

            margin-bottom: 8px;
        }


        .dashboard-card-title {

            color: #344054;

            font-size: 13px;

            font-weight: 600;
        }


        .dashboard-card-icon {

            width: 34px;

            height: 34px;

            display: flex;

            align-items: center;

            justify-content: center;

            border-radius: 8px;

            font-size: 17px;

            background: #EAF1F5;
        }


        /* Icon variants */

        .icon-purple {

            background: #EAF1F5;
        }


        .icon-blue {

            background: #EAF1F5;
        }


        .icon-orange {

            background: #FFF4E5;
        }


        .icon-red {

            background: #FDECEC;
        }


        .icon-cyan {

            background: #E9F7F8;
        }


        /* =========================================================
        CARD VALUE
        ========================================================= */

        .dashboard-card-value {

            color: #063552;

            font-size: 27px;

            font-weight: 800;

            line-height: 1.2;

            margin-top: 4px;

            margin-bottom: 7px;
        }


        /* =========================================================
        CARD FOOTER
        ========================================================= */

        .dashboard-card-footer {

            font-size: 12px;

            font-weight: 700;

            line-height: 1.3;
        }


        .status-positive {

            color: #16A34A !important;
        }


        .status-warning {

            color: #D97706 !important;
        }


        .status-danger {

            color: #DC2626 !important;
        }


        /* =========================================================
        CHART CARD
        ========================================================= */

        .dashboard-chart-card {

            background: #FFFFFF;

            border: 1px solid #D0D7DE;

            border-radius: 12px;

            padding: 12px 14px 8px;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.07);

            overflow: hidden;
        }


        .chart-title {

            color: #063552;

            font-size: 16px;

            font-weight: 800;

            padding: 4px 2px 8px;
        }


        /* =========================================================
        QUICK ACTIONS
        ========================================================= */

        .quick-actions-card {

            background: #FFFFFF;

            border: 1px solid #D0D7DE;

            border-radius: 12px;

            padding: 16px;

            margin-top: 18px;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.07);
        }



        /* =========================================================
        STANDARD PAGE HEADER
        ========================================================= */

        .page-title {

            color: #063552;

            font-size: 30px;

            font-weight: 800;

            line-height: 1.2;

            margin-bottom: 4px;
        }


        .page-subtitle {

            color: #667085;

            font-size: 14px;

            margin-bottom: 22px;
        }



        /* =========================================================
        GUARDS PAGE
        COMPANY SETTINGS STYLE
        ========================================================= */


        /* PAGE HEADER */

        .page-title {

            color: #063552;

            font-size: 30px;

            font-weight: 800;

            line-height: 1.2;

            margin-bottom: 4px;
        }


        .page-subtitle {

            color: #667085;

            font-size: 14px;

            margin-bottom: 22px;
        }


        /* =========================================================
        TABS
        ========================================================= */

        .stTabs [data-baseweb="tab-list"] {

            gap: 4px;

            border-bottom:
                1px solid #D0D7DE;

            margin-bottom: 18px;
        }


        .stTabs [data-baseweb="tab"] {

            color:
                #344054 !important;

            font-weight:
                600 !important;

            padding:
                10px 18px !important;

            border-radius:
                7px 7px 0 0 !important;
        }


        .stTabs [data-baseweb="tab"]:hover {

            color:
                #063552 !important;

            background:
                #EAF1F5 !important;
        }


        .stTabs [data-baseweb="tab"][aria-selected="true"] {

            color:
                #063552 !important;

            background:
                #E1E8ED !important;

            font-weight:
                800 !important;
        }


        .stTabs [data-baseweb="tab-highlight"] {

            background:
                #69DA25 !important;

            height:
                3px !important;
        }


        /* =========================================================
        SECTION HEADER
        ========================================================= */

        .dashboard-section-title {

            background:
                #E1E8ED !important;

            color:
                #063552 !important;

            font-size:
                18px !important;

            font-weight:
                800 !important;

            padding:
                9px 14px !important;

            border-radius:
                8px !important;

            border-left:
                4px solid #69DA25 !important;

            margin-top:
                18px !important;

            margin-bottom:
                16px !important;
        }


        /* =========================================================
        METRIC CARDS
        ========================================================= */

        div[data-testid="stMetric"] {

            background:
                #FFFFFF !important;

            border:
                1px solid #D0D7DE !important;

            border-radius:
                10px !important;

            padding:
                16px 18px !important;

            min-height:
                105px !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.07) !important;
        }


        div[data-testid="stMetricLabel"] p {

            color:
                #344054 !important;

            font-weight:
                600 !important;
        }


        div[data-testid="stMetricValue"] {

            color:
                #063552 !important;

            font-weight:
                800 !important;
        }


        /* =========================================================
        INPUTS
        ========================================================= */

        .stTextInput > div > div,
        .stTextArea > div > div,
        .stNumberInput > div > div,
        .stDateInput > div > div {

            background:
                #FFFFFF !important;

            border:
                1px solid #B8C2CC !important;

            border-radius:
                8px !important;

            box-shadow:
                0 1px 3px rgba(6, 53, 82, 0.08) !important;
        }


        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input,
        .stDateInput input {

            color:
                #17202A !important;

            background:
                #FFFFFF !important;
        }


        /* =========================================================
        SELECTBOX
        ========================================================= */

        div[data-baseweb="select"] > div {

            background:
                #FFFFFF !important;

            border:
                1px solid #B8C2CC !important;

            border-radius:
                8px !important;

            box-shadow:
                0 1px 3px rgba(6, 53, 82, 0.08) !important;
        }


        /* =========================================================
        FORM
        ========================================================= */

        div[data-testid="stForm"] {

            background:
                #FFFFFF !important;

            border:
                1px solid #D0D7DE !important;

            border-radius:
                12px !important;

            padding:
                22px !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.07) !important;
        }


        /* =========================================================
        FORM SECTION HEADERS
        ========================================================= */

        div[data-testid="stForm"] h3,
        div[data-testid="stForm"] h4 {

            background:
                #E1E8ED !important;

            color:
                #063552 !important;

            font-weight:
                800 !important;

            padding:
                9px 14px !important;

            border-radius:
                7px !important;

            border-left:
                4px solid #69DA25 !important;
        }


        /* =========================================================
        DATAFRAME
        ========================================================= */

        div[data-testid="stDataFrame"] {

            background:
                #FFFFFF !important;

            border:
                1px solid #CBD5DC !important;

            border-radius:
                10px !important;

            overflow:
                hidden !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.07) !important;
        }


        /* =========================================================
        BUTTONS
        ========================================================= */

        .stButton > button,
        .stFormSubmitButton > button {

            min-height:
                42px !important;

            border-radius:
                8px !important;

            font-weight:
                700 !important;
        }


        .stButton > button[kind="primary"],
        .stFormSubmitButton > button[kind="primary"] {

            background:
                #063552 !important;

            color:
                #FFFFFF !important;

            border:
                1px solid #063552 !important;

            box-shadow:
                0 2px 5px rgba(6, 53, 82, 0.15) !important;
        }


        .stButton > button[kind="primary"]:hover,
        .stFormSubmitButton > button[kind="primary"]:hover {

            background:
                #04283E !important;

            border-color:
                #04283E !important;
        }


        /* =========================================================
        FILE UPLOADER
        ========================================================= */

        div[data-testid="stFileUploader"] {

            background:
                #FFFFFF !important;

            border:
                1px solid #D0D7DE !important;

            border-radius:
                10px !important;

            padding:
                8px !important;

            box-shadow:
                0 1px 4px rgba(6, 53, 82, 0.06) !important;
        }


        /* =========================================================
        DIVIDERS
        ========================================================= */

        hr {

            border-top:
                1px solid #D0D7DE !important;
        }



        /* =========================================================
        TEXT AREA - FIX
        ========================================================= */

        /* Main text area container */
        div[data-testid="stTextArea"] {
            width: 100% !important;
        }

        /* Outer wrapper */
        div[data-testid="stTextArea"] > div {
            background: #FFFFFF !important;
            border: 1px solid #B8C2CC !important;
            border-radius: 8px !important;
            box-shadow: 0 1px 3px rgba(6, 53, 82, 0.08) !important;
            overflow: hidden !important;
        }

        /* Textarea itself */
        div[data-testid="stTextArea"] textarea {
            display: block !important;

            width: 100% !important;

            min-height: 110px !important;

            background: #FFFFFF !important;

            color: #17202A !important;

            border: none !important;

            outline: none !important;

            box-shadow: none !important;

            padding: 12px !important;

            font-size: 14px !important;

            line-height: 1.5 !important;

            resize: vertical !important;
        }

        /* Placeholder */
        div[data-testid="stTextArea"] textarea::placeholder {
            color: #667085 !important;
            opacity: 1 !important;
        }

        /* Focus */
        div[data-testid="stTextArea"]:focus-within > div {
            border-color: #063552 !important;

            box-shadow:
                0 0 0 2px rgba(6, 53, 82, 0.10) !important;
        }



        /* =========================================================
        TEXT INPUT / NUMBER INPUT / DATE INPUT
        ========================================================= */

        div[data-testid="stTextInput"] > div,
        div[data-testid="stNumberInput"] > div,
        div[data-testid="stDateInput"] > div {

            background: #FFFFFF !important;

            border: 1px solid #B8C2CC !important;

            border-radius: 8px !important;

            box-shadow:
                0 1px 3px rgba(6, 53, 82, 0.08) !important;
        }


        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input {

            background: #FFFFFF !important;

            color: #17202A !important;

            border: none !important;

            box-shadow: none !important;
        }


        div[data-testid="stTextInput"]:focus-within > div,
        div[data-testid="stNumberInput"]:focus-within > div,
        div[data-testid="stDateInput"]:focus-within > div {

            border-color: #063552 !important;

            box-shadow:
                0 0 0 2px rgba(6, 53, 82, 0.10) !important;
        }





        /* =========================================================
        GUARD WORK MANAGEMENT
        COMPANY SETTINGS STYLE
        ========================================================= */

        :root {
            --primary: #063552;
            --primary-dark: #04283e;
            --secondary: #56d21f;
            --page-bg: #f4f7f9;
            --section-bg: #e7edf1;
            --card-bg: #ffffff;
            --border: #c7d0d8;
            --text: #063552;
            --muted: #667085;
            --shadow-sm: 0 2px 6px rgba(6, 53, 82, 0.10);
            --shadow-md: 0 4px 12px rgba(6, 53, 82, 0.12);
        }


        /* =========================================================
        PAGE
        ========================================================= */

        [data-testid="stAppViewContainer"] {
            background: var(--page-bg) !important;
        }

        .main .block-container {
            max-width: 1400px !important;
            padding-top: 25px !important;
            padding-bottom: 40px !important;
        }


        /* =========================================================
        PAGE TITLE
        ========================================================= */

        h1 {
            color: var(--primary) !important;
            font-weight: 800 !important;
            letter-spacing: -0.4px !important;
        }

        h2,
        h3 {
            color: var(--primary) !important;
            font-weight: 700 !important;
        }

        [data-testid="stCaptionContainer"] {
            color: #667085 !important;
        }


        /* =========================================================
        TABS
        ========================================================= */

        button[data-baseweb="tab"] {
            color: var(--primary) !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            padding: 12px 18px !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--primary) !important;
            font-weight: 800 !important;
        }

        div[data-baseweb="tab-highlight"] {
            background-color: var(--secondary) !important;
            height: 3px !important;
        }

        div[data-baseweb="tab-border"] {
            background-color: #cbd5dc !important;
        }


        /* =========================================================
        SECTION HEADERS
        Matches Company Settings
        ========================================================= */

        .guard-section-header {
            background: var(--section-bg);
            border-left: 5px solid var(--secondary);
            border-radius: 8px;
            padding: 10px 15px;
            margin: 18px 0 15px 0;

            color: var(--primary);
            font-size: 19px;
            font-weight: 800;

            box-shadow: none;
        }


        /* =========================================================
        INPUT LABELS
        ========================================================= */

        label {
            color: var(--primary) !important;
            font-weight: 600 !important;
        }


        /* =========================================================
        TEXT INPUT
        ========================================================= */

        div[data-testid="stTextInput"] > div {
            background: #ffffff !important;
            border: 1px solid #b8c4ce !important;
            border-radius: 8px !important;
            box-shadow: var(--shadow-sm) !important;
        }

        div[data-testid="stTextInput"] input {
            background: #ffffff !important;
            color: #17202a !important;
            border: none !important;
            box-shadow: none !important;
        }

        div[data-testid="stTextInput"]:focus-within > div {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(6, 53, 82, 0.10) !important;
        }


        /* =========================================================
        NUMBER INPUT
        ========================================================= */

        div[data-testid="stNumberInput"] > div {
            background: #ffffff !important;
            border: 1px solid #b8c4ce !important;
            border-radius: 8px !important;
            box-shadow: var(--shadow-sm) !important;
        }

        div[data-testid="stNumberInput"] input {
            background: #ffffff !important;
            color: #17202a !important;
        }


        /* =========================================================
        DATE INPUT
        ========================================================= */

        div[data-testid="stDateInput"] > div {
            background: #ffffff !important;
            border: 1px solid #b8c4ce !important;
            border-radius: 8px !important;
            box-shadow: var(--shadow-sm) !important;
        }

        div[data-testid="stDateInput"] input {
            background: #ffffff !important;
            color: #17202a !important;
        }


        /* =========================================================
        SELECTBOX
        ========================================================= */

        div[data-testid="stSelectbox"] > div > div {
            background: #ffffff !important;
            border: 1px solid #b8c4ce !important;
            border-radius: 8px !important;
            box-shadow: var(--shadow-sm) !important;
        }

        div[data-testid="stSelectbox"] [role="combobox"] {
            color: var(--primary) !important;
        }


        /* =========================================================
        TEXT AREA
        ========================================================= */

        div[data-testid="stTextArea"] > div {
            background: #ffffff !important;
            border: 1px solid #b8c4ce !important;
            border-radius: 8px !important;
            box-shadow: var(--shadow-sm) !important;
            overflow: hidden !important;
        }

        div[data-testid="stTextArea"] textarea {
            background: #ffffff !important;
            color: #17202a !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;

            min-height: 110px !important;
            padding: 12px !important;
        }

        div[data-testid="stTextArea"]:focus-within > div {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(6, 53, 82, 0.10) !important;
        }


        /* =========================================================
        METRIC CARDS
        ========================================================= */

        div[data-testid="stMetric"] {
            background: #ffffff !important;

            border: 1px solid var(--border) !important;

            border-radius: 10px !important;

            padding: 15px 17px !important;

            min-height: 105px !important;

            box-shadow: var(--shadow-sm) !important;
        }

        div[data-testid="stMetricLabel"] {
            color: var(--primary) !important;
            font-size: 13px !important;
            font-weight: 600 !important;
        }

        div[data-testid="stMetricValue"] {
            color: var(--primary) !important;
            font-size: 26px !important;
            font-weight: 800 !important;
        }


        /* =========================================================
        BUTTONS
        ========================================================= */

        .stButton > button {
            border-radius: 8px !important;

            min-height: 42px !important;

            font-weight: 700 !important;

            border: 1px solid var(--primary) !important;

            box-shadow: var(--shadow-sm) !important;

            transition:
                transform 0.12s ease,
                box-shadow 0.12s ease !important;
        }

        .stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: var(--shadow-md) !important;
        }


        /* Primary buttons */

        .stButton > button[kind="primary"] {
            background: var(--primary) !important;
            color: #ffffff !important;
        }

        .stButton > button[kind="primary"]:hover {
            background: var(--primary-dark) !important;
        }


        /* Secondary buttons */

        .stButton > button[kind="secondary"] {
            background: #ffffff !important;
            color: var(--primary) !important;
        }


        /* =========================================================
        DATAFRAME
        ========================================================= */

        div[data-testid="stDataFrame"] {
            border: 1px solid #c7d0d8 !important;
            border-radius: 10px !important;
            overflow: hidden !important;
            box-shadow: var(--shadow-sm) !important;
            background: #ffffff !important;
        }


        /* dataframe header */

        div[data-testid="stDataFrame"] [role="columnheader"] {
            background: #dfe7ec !important;
            color: var(--primary) !important;
            font-weight: 800 !important;
            border-bottom: 1px solid #b8c4ce !important;
        }


        /* dataframe cells */

        div[data-testid="stDataFrame"] [role="gridcell"] {
            color: #173042 !important;
            background: #ffffff !important;
            border-color: #d7dee4 !important;
        }


        /* =========================================================
        DIVIDERS
        ========================================================= */

        hr {
            border: none !important;
            border-top: 1px solid #cbd4db !important;
            margin: 22px 0 !important;
        }


        /* =========================================================
        INFO / WARNING / SUCCESS
        ========================================================= */

        div[data-testid="stAlert"] {
            border-radius: 8px !important;
            border: 1px solid #cbd5dc !important;
            box-shadow: var(--shadow-sm) !important;
        }


        /* =========================================================
        RADIO
        ========================================================= */

        div[data-testid="stRadio"] label {
            font-weight: 600 !important;
            color: var(--primary) !important;
        }


        /* =========================================================
        SMALL HEADINGS
        ========================================================= */

        .stMarkdown h3 {
            color: var(--primary) !important;
            font-weight: 800 !important;
        }


        /* =========================================================
        GUARD WORK TAB CONTENT SPACING
        ========================================================= */

        [data-testid="stTabs"] [data-baseweb="tab-panel"] {
            padding-top: 18px !important;
        }


        /* =========================================================
        DELETE SECTION
        ========================================================= */

        .delete-section {
            background: #ffffff;
            border: 1px solid #d5dce2;
            border-radius: 10px;
            padding: 16px;
            margin-top: 15px;
            box-shadow: var(--shadow-sm);
        }


        /* =========================================================
        MOBILE
        ========================================================= */

        @media (max-width: 768px) {

            .main .block-container {
                padding-left: 12px !important;
                padding-right: 12px !important;
            }

            button[data-baseweb="tab"] {
                font-size: 12px !important;
                padding: 10px 8px !important;
            }

            div[data-testid="stMetric"] {
                min-height: 90px !important;
            }

            div[data-testid="stMetricValue"] {
                font-size: 22px !important;
            }
        }


        /* =========================================================
        PAGE HEADER
        ========================================================= */

        .page-header {
            background: #ffffff;

            border: 1px solid #cbd4db;

            border-radius: 10px;

            padding: 18px 22px;

            margin-bottom: 18px;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08);

            border-left: 5px solid #56d21f;
        }

        .page-header-title {
            color: #063552;

            font-size: 27px;

            font-weight: 800;

            line-height: 1.2;
        }

        .page-header-subtitle {
            color: #667085;

            font-size: 14px;

            margin-top: 6px;
        }


        /* =========================================================
        SITE MANAGEMENT
        COMPANY SETTINGS STYLE
        ========================================================= */

        /* =========================================================
        SITE PAGE HEADER
        ========================================================= */

        .site-page-header {
            width: 100%;

            background: #FFFFFF;

            border: 1px solid #CBD4DB;

            border-left: 5px solid #56D21F;

            border-radius: 10px;

            padding: 18px 22px;

            margin: 0 0 22px 0;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08);

            box-sizing: border-box;
        }


        .site-page-title {
            color: #063552;

            font-size: 28px;

            font-weight: 800;

            line-height: 1.25;

            margin: 0;
        }


        .site-page-subtitle {
            color: #667085;

            font-size: 14px;

            font-weight: 400;

            line-height: 1.5;

            margin-top: 5px;
        }


        /* ---------------------------------------------------------
        SECTION HEADER
        SAME AS COMPANY SETTINGS
        --------------------------------------------------------- */

        .site-section-header {
            background: #e7edf1;

            border-left: 5px solid #56d21f;

            border-radius: 8px;

            padding: 10px 15px;

            margin: 18px 0 15px 0;

            color: #063552;

            font-size: 19px;

            font-weight: 800;
        }


        /* ---------------------------------------------------------
        TABS
        --------------------------------------------------------- */

        button[data-baseweb="tab"] {
            color: #063552 !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            padding: 12px 18px !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #063552 !important;
            font-weight: 800 !important;
        }

        div[data-baseweb="tab-highlight"] {
            background-color: #56d21f !important;
            height: 3px !important;
        }

        div[data-baseweb="tab-border"] {
            background-color: #cbd5dc !important;
        }


        /* ---------------------------------------------------------
        LABELS
        --------------------------------------------------------- */

        label {
            color: #063552 !important;
            font-weight: 600 !important;
        }


        /* ---------------------------------------------------------
        TEXT INPUT
        --------------------------------------------------------- */

        div[data-testid="stTextInput"] > div {
            background: #ffffff !important;
            border: 1px solid #b8c4ce !important;
            border-radius: 8px !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08) !important;
        }

        div[data-testid="stTextInput"] input {
            background: #ffffff !important;
            color: #17202a !important;
            border: none !important;
            box-shadow: none !important;
        }

        div[data-testid="stTextInput"]:focus-within > div {
            border-color: #063552 !important;

            box-shadow:
                0 0 0 2px rgba(6, 53, 82, 0.10) !important;
        }


        /* ---------------------------------------------------------
        NUMBER INPUT
        --------------------------------------------------------- */

        div[data-testid="stNumberInput"] > div {
            background: #ffffff !important;
            border: 1px solid #b8c4ce !important;
            border-radius: 8px !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08) !important;
        }

        div[data-testid="stNumberInput"] input {
            background: #ffffff !important;
            color: #17202a !important;
        }


        /* ---------------------------------------------------------
        SELECTBOX
        --------------------------------------------------------- */

        div[data-testid="stSelectbox"] > div > div {
            background: #ffffff !important;
            border: 1px solid #b8c4ce !important;
            border-radius: 8px !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08) !important;
        }

        div[data-testid="stSelectbox"] [role="combobox"] {
            color: #063552 !important;
        }


        /* ---------------------------------------------------------
        TEXT AREA
        --------------------------------------------------------- */

        div[data-testid="stTextArea"] > div {
            background: #ffffff !important;
            border: 1px solid #b8c4ce !important;
            border-radius: 8px !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08) !important;

            overflow: hidden !important;
        }

        div[data-testid="stTextArea"] textarea {
            background: #ffffff !important;
            color: #17202a !important;

            border: none !important;
            outline: none !important;
            box-shadow: none !important;

            min-height: 110px !important;
            padding: 12px !important;
        }

        div[data-testid="stTextArea"]:focus-within > div {
            border-color: #063552 !important;

            box-shadow:
                0 0 0 2px rgba(6, 53, 82, 0.10) !important;
        }


        /* ---------------------------------------------------------
        FORMS
        --------------------------------------------------------- */

        div[data-testid="stForm"] {
            background: #ffffff !important;

            border: 1px solid #cbd4db !important;

            border-radius: 10px !important;

            padding: 20px !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08) !important;
        }


        /* ---------------------------------------------------------
        METRICS
        --------------------------------------------------------- */

        div[data-testid="stMetric"] {
            background: #ffffff !important;

            border: 1px solid #c7d0d8 !important;

            border-radius: 10px !important;

            padding: 15px 17px !important;

            min-height: 105px !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08) !important;
        }

        div[data-testid="stMetricLabel"] {
            color: #063552 !important;

            font-size: 13px !important;

            font-weight: 600 !important;
        }

        div[data-testid="stMetricValue"] {
            color: #063552 !important;

            font-size: 26px !important;

            font-weight: 800 !important;
        }


        /* ---------------------------------------------------------
        BUTTONS
        --------------------------------------------------------- */

        .stButton > button,
        button[kind="primaryFormSubmit"] {
            border-radius: 8px !important;

            min-height: 42px !important;

            font-weight: 700 !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.10) !important;

            transition:
                transform 0.12s ease,
                box-shadow 0.12s ease !important;
        }

        .stButton > button:hover,
        button[kind="primaryFormSubmit"]:hover {
            transform: translateY(-1px) !important;

            box-shadow:
                0 4px 12px rgba(6, 53, 82, 0.14) !important;
        }


        /* Primary */

        .stButton > button[kind="primary"],
        button[kind="primaryFormSubmit"] {
            background: #063552 !important;
            color: #ffffff !important;

            border: 1px solid #063552 !important;
        }

        .stButton > button[kind="primary"]:hover,
        button[kind="primaryFormSubmit"]:hover {
            background: #04283e !important;
        }


        /* ---------------------------------------------------------
        DATAFRAME
        --------------------------------------------------------- */

        div[data-testid="stDataFrame"] {
            border: 1px solid #c7d0d8 !important;

            border-radius: 10px !important;

            overflow: hidden !important;

            background: #ffffff !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08) !important;
        }


        /* Header */

        div[data-testid="stDataFrame"] [role="columnheader"] {
            background: #dfe7ec !important;

            color: #063552 !important;

            font-weight: 800 !important;

            border-bottom: 1px solid #b8c4ce !important;
        }


        /* Cells */

        div[data-testid="stDataFrame"] [role="gridcell"] {
            background: #ffffff !important;

            color: #173042 !important;

            border-color: #d7dee4 !important;
        }


        /* ---------------------------------------------------------
        DIVIDERS
        --------------------------------------------------------- */

        hr {
            border: none !important;

            border-top: 1px solid #cbd4db !important;

            margin: 22px 0 !important;
        }


        /* ---------------------------------------------------------
        INFO / WARNING / SUCCESS
        --------------------------------------------------------- */

        div[data-testid="stAlert"] {
            border-radius: 8px !important;

            border: 1px solid #cbd5dc !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.06) !important;
        }


        /* ---------------------------------------------------------
        EXPANDER
        --------------------------------------------------------- */

        div[data-testid="stExpander"] {
            background: #ffffff !important;

            border: 1px solid #cbd4db !important;

            border-radius: 10px !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.06) !important;
        }

        div[data-testid="stExpander"] summary {
            color: #063552 !important;

            font-weight: 700 !important;
        }


        /* ---------------------------------------------------------
        SITE ASSIGNMENT CARD
        --------------------------------------------------------- */

        .site-guard-card {
            background: #ffffff;

            border: 1px solid #cbd4db;

            border-radius: 10px;

            padding: 14px 16px;

            margin: 8px 0;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.07);
        }


        /* ---------------------------------------------------------
        MOBILE
        --------------------------------------------------------- */

        @media (max-width: 768px) {

            .main .block-container {
                padding-left: 12px !important;
                padding-right: 12px !important;
            }

            button[data-baseweb="tab"] {
                font-size: 12px !important;
                padding: 10px 8px !important;
            }

            div[data-testid="stMetric"] {
                min-height: 90px !important;
            }

            div[data-testid="stMetricValue"] {
                font-size: 22px !important;
            }
        }



        /* =========================================================
        BILLING & PAYROLL
        COMPANY SETTINGS STYLE
        ========================================================= */


        /* =========================================================
        PAGE HEADER
        ========================================================= */

        .billing-page-header {
            width: 100%;

            background: #ffffff;

            border: 1px solid #cbd4db;
            border-left: 5px solid #56d21f;

            border-radius: 10px;

            padding: 18px 22px;

            margin: 0 0 22px 0;

            box-sizing: border-box;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08);
        }


        .billing-page-title {
            color: #063552;

            font-size: 28px;

            font-weight: 800;

            line-height: 1.25;
        }


        .billing-page-subtitle {
            color: #667085;

            font-size: 14px;

            font-weight: 400;

            line-height: 1.5;

            margin-top: 5px;
        }


        /* =========================================================
        TABS
        ========================================================= */

        button[data-baseweb="tab"] {
            color: #063552 !important;

            font-size: 14px !important;

            font-weight: 600 !important;

            padding: 12px 18px !important;
        }


        button[data-baseweb="tab"][aria-selected="true"] {
            color: #063552 !important;

            font-weight: 800 !important;
        }


        div[data-baseweb="tab-highlight"] {
            background: #56d21f !important;

            height: 3px !important;
        }


        div[data-baseweb="tab-border"] {
            background: #cbd4db !important;
        }


        /* =========================================================
        SECTION HEADERS
        ========================================================= */

        .billing-section-header {
            background: #e7edf1;

            border-left: 5px solid #56d21f;

            border-radius: 8px;

            padding: 10px 15px;

            margin: 20px 0 15px 0;

            color: #063552;

            font-size: 19px;

            font-weight: 800;

            line-height: 1.3;
        }


        /* =========================================================
        FORM CARD
        ========================================================= */

        div[data-testid="stForm"] {

            background: #ffffff !important;

            border: 1px solid #cbd4db !important;

            border-radius: 10px !important;

            padding: 20px !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08) !important;
        }


        /* =========================================================
        LABELS
        ========================================================= */

        div[data-testid="stTextInput"] label,
        div[data-testid="stNumberInput"] label,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stDateInput"] label {

            color: #063552 !important;

            font-weight: 600 !important;

            font-size: 14px !important;
        }


        /* =========================================================
        TEXT INPUT
        ========================================================= */

        div[data-testid="stTextInput"] > div {

            background: #ffffff !important;

            border: 1px solid #b8c4ce !important;

            border-radius: 8px !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08) !important;
        }


        div[data-testid="stTextInput"] input {

            background: #ffffff !important;

            color: #17202a !important;

            font-size: 14px !important;

            border: none !important;

            box-shadow: none !important;
        }


        div[data-testid="stTextInput"]:focus-within > div {

            border-color: #063552 !important;

            box-shadow:
                0 0 0 2px rgba(6, 53, 82, 0.10) !important;
        }


        /* =========================================================
        NUMBER INPUT
        ========================================================= */

        div[data-testid="stNumberInput"] > div {

            background: #ffffff !important;

            border: 1px solid #b8c4ce !important;

            border-radius: 8px !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08) !important;
        }


        div[data-testid="stNumberInput"] input {

            background: #ffffff !important;

            color: #17202a !important;

            font-size: 14px !important;
        }


        /* =========================================================
        SELECT BOX
        ========================================================= */

        div[data-testid="stSelectbox"] > div > div {

            background: #ffffff !important;

            border: 1px solid #b8c4ce !important;

            border-radius: 8px !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08) !important;
        }


        div[data-testid="stSelectbox"] [role="combobox"] {

            color: #063552 !important;

            font-weight: 500 !important;
        }


        /* =========================================================
        DATE INPUT
        ========================================================= */

        div[data-testid="stDateInput"] > div > div {

            background: #ffffff !important;

            border: 1px solid #b8c4ce !important;

            border-radius: 8px !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08) !important;
        }


        /* =========================================================
        METRIC CARDS
        ========================================================= */

        div[data-testid="stMetric"] {

            background: #ffffff !important;

            border: 1px solid #c7d0d8 !important;

            border-radius: 10px !important;

            padding: 16px 18px !important;

            min-height: 105px !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08) !important;
        }


        div[data-testid="stMetricLabel"] {

            color: #063552 !important;

            font-size: 13px !important;

            font-weight: 600 !important;
        }


        div[data-testid="stMetricValue"] {

            color: #063552 !important;

            font-size: 25px !important;

            font-weight: 800 !important;
        }


        /* =========================================================
        PRIMARY BUTTON
        ========================================================= */

        .stButton > button[kind="primary"] {

            background: #063552 !important;

            color: #ffffff !important;

            border: 1px solid #063552 !important;

            border-radius: 8px !important;

            min-height: 42px !important;

            font-weight: 700 !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.15) !important;
        }


        .stButton > button[kind="primary"]:hover {

            background: #04283e !important;

            border-color: #04283e !important;

            transform: translateY(-1px);
        }


        /* =========================================================
        NORMAL BUTTONS
        ========================================================= */

        .stButton > button {

            border-radius: 8px !important;

            min-height: 40px !important;

            font-weight: 600 !important;

            color: #063552 !important;

            border: 1px solid #b8c4ce !important;

            background: #ffffff !important;

            box-shadow:
                0 2px 5px rgba(6, 53, 82, 0.07) !important;
        }


        .stButton > button:hover {

            border-color: #063552 !important;

            background: #f5f8fa !important;

            color: #063552 !important;
        }


        /* =========================================================
        DOWNLOAD BUTTON
        ========================================================= */

        .stDownloadButton > button {

            width: 100% !important;

            min-height: 40px !important;

            border-radius: 8px !important;

            font-weight: 700 !important;

            color: #063552 !important;

            background: #ffffff !important;

            border: 1px solid #b8c4ce !important;

            box-shadow:
                0 2px 5px rgba(6, 53, 82, 0.07) !important;
        }


        .stDownloadButton > button:hover {

            background: #f5f8fa !important;

            border-color: #063552 !important;
        }


        /* =========================================================
        DATAFRAME
        ========================================================= */

        div[data-testid="stDataFrame"] {

            background: #ffffff !important;

            border: 1px solid #c7d0d8 !important;

            border-radius: 10px !important;

            overflow: hidden !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.08) !important;
        }


        /* DataFrame header */

        div[data-testid="stDataFrame"]
        [role="columnheader"] {

            background: #dfe7ec !important;

            color: #063552 !important;

            font-weight: 800 !important;

            border-bottom: 1px solid #b8c4ce !important;
        }


        /* DataFrame cells */

        div[data-testid="stDataFrame"]
        [role="gridcell"] {

            background: #ffffff !important;

            color: #173042 !important;

            border-color: #d7dee4 !important;
        }


        /* =========================================================
        INFO / WARNING / SUCCESS
        ========================================================= */

        div[data-testid="stAlert"] {

            border-radius: 8px !important;

            border: 1px solid #cbd4db !important;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.06) !important;
        }


        /* =========================================================
        DIVIDERS
        ========================================================= */

        hr {

            border: none !important;

            border-top: 1px solid #cbd4db !important;

            margin: 22px 0 !important;
        }


        /* =========================================================
        BILL / SALARY ACTION AREA
        ========================================================= */

        .billing-actions {

            background: #ffffff;

            border: 1px solid #cbd4db;

            border-radius: 10px;

            padding: 14px;

            margin-top: 15px;

            box-shadow:
                0 2px 6px rgba(6, 53, 82, 0.07);
        }


        /* =========================================================
        RESPONSIVE
        ========================================================= */

        @media (max-width: 768px) {

            .billing-page-title {
                font-size: 23px;
            }

            .billing-page-subtitle {
                font-size: 13px;
            }

            button[data-baseweb="tab"] {
                font-size: 12px !important;

                padding: 10px 8px !important;
            }

            div[data-testid="stMetric"] {
                min-height: 90px !important;

                padding: 12px !important;
            }

            div[data-testid="stMetricValue"] {
                font-size: 21px !important;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )