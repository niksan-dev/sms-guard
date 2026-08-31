import streamlit as st
import pandas as pd

from datetime import date

from components.page_header import page_header
from components.sub_header import sub_header
from components.text_input import text_input
from components.number_input import number_input
from components.select_box import select_box
from components.date_input import date_input
from components.text_area import text_area
from components.search_box import search_box
from components.button import button

from services.guard_service import (
    get_all_guards,
    get_available_guard_users,
    get_next_employee_id,
    get_guard_by_id,
    get_guard_photo_path,
    create_guard,
    update_guard,
)

from services.site_guard_assignment_service import (
    assign_guard_to_site,
    get_guard_sites,
    unassign_guard_from_site
)

from services.site_service import get_all_sites


# ==================================================
# MASK AADHAAR
# ==================================================

def mask_aadhaar(aadhaar_number):

    if not aadhaar_number:
        return ""

    aadhaar_number = str(aadhaar_number).replace(" ", "")

    if len(aadhaar_number) != 12:
        return "****"

    return f"XXXX XXXX {aadhaar_number[-4:]}"


# ==================================================
# VALIDATE PHONE
# ==================================================

def validate_phone(phone):

    phone = phone.strip()

    if not phone:
        return False, "Phone number is required."

    if not phone.isdigit():
        return False, "Phone number must contain digits only."

    if len(phone) != 10:
        return False, "Phone number must contain exactly 10 digits."

    return True, ""


# ==================================================
# VALIDATE PIN CODE
# ==================================================

def validate_pincode(pincode):

    pincode = pincode.strip()

    if not pincode:
        return False, "PIN code is required."

    if not pincode.isdigit():
        return False, "PIN code must contain digits only."

    if len(pincode) != 6:
        return False, "PIN code must contain exactly 6 digits."

    return True, ""


# ==================================================
# VALIDATE AADHAAR
# ==================================================

def validate_aadhaar(aadhaar_number):

    aadhaar_number = (
        aadhaar_number
        .strip()
        .replace(" ", "")
    )

    if not aadhaar_number:
        return False, "Aadhaar number is required."

    if not aadhaar_number.isdigit():
        return False, "Aadhaar number must contain digits only."

    if len(aadhaar_number) != 12:
        return False, "Aadhaar number must contain exactly 12 digits."

    return True, ""


# ==================================================
# SHOW GUARDS
# ==================================================

def show_guards():

    # ==================================================
    # PAGE HEADER
    # ==================================================


    page_header("Guard Management","","👮")

    # ==================================================
    # TABS
    # ==================================================

    tab1, tab2, tab3 = st.tabs([
        "📋 All Guards",
        "➕ Add Guard",
        "⚙️ Manage Guard"
    ])

    # ==================================================
    # TAB 1 - ALL GUARDS
    # ==================================================

    with tab1:

        sub_header("All Guards","","📋")

        guards = get_all_guards()

        if not guards:

            st.info(
                "No guards found. "
                "Add your first guard from the Add Guard tab."
            )

        else:

            # ----------------------------------------------
            # GUARD DATA
            # ----------------------------------------------

            guard_data = []

            for guard in guards:

                monthly_salary = float(
                    getattr(guard, "monthly_salary", 0) or 0
                )

                guard_data.append({

                    "Employee ID":
                        guard.employee_id or "",

                    "Name":
                        guard.name or "",

                    "Phone":
                        guard.phone or "",

                    "Email":
                        guard.email or "",

                    "Monthly Salary (₹)":
                        monthly_salary,

                    "PIN Code":
                        guard.pincode or "",

                    "Joining Date":
                        guard.joining_date,

                    "Status":
                        guard.status or ""
                })

            df = pd.DataFrame(guard_data)

            # ----------------------------------------------
            # SEARCH
            # ----------------------------------------------

            search = search_box(
                "🔍 Search Guard",
                placeholder=(
                    "Search by employee ID, name, "
                    "phone or status..."
                ),
                key="guard_search"
            )

            if search:

                search = search.lower()

                mask = (

                    df["Employee ID"]
                    .astype(str)
                    .str.lower()
                    .str.contains(search, na=False)

                    |

                    df["Name"]
                    .astype(str)
                    .str.lower()
                    .str.contains(search, na=False)

                    |

                    df["Phone"]
                    .astype(str)
                    .str.lower()
                    .str.contains(search, na=False)

                    |

                    df["Email"]
                    .astype(str)
                    .str.lower()
                    .str.contains(search, na=False)

                    |

                    df["Status"]
                    .astype(str)
                    .str.lower()
                    .str.contains(search, na=False)
                )

                df = df[mask]

            # ----------------------------------------------
            # SUMMARY
            # ----------------------------------------------

            total_guards = len(df)

            active_guards = len(
                df[
                    df["Status"]
                    .astype(str)
                    .str.lower() == "active"
                ]
            )

            total_monthly_salary = (
                df["Monthly Salary (₹)"].sum()
                if not df.empty
                else 0
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "👮 Total Guards",
                    total_guards
                )

            with col2:

                st.metric(
                    "🟢 Active Guards",
                    active_guards
                )

            with col3:

                st.metric(
                    "💰 Monthly Salary Cost",
                    f"₹ {total_monthly_salary:,.2f}"
                )

            # ----------------------------------------------
            # TABLE
            # ----------------------------------------------

            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                column_config={

                    "Monthly Salary (₹)": st.column_config.NumberColumn(
                        "Monthly Salary (₹)",
                        format="₹ %.2f"
                    ),

                    "Joining Date": st.column_config.DateColumn(
                        "Joining Date"
                    )
                }
            )

            st.caption(
                f"Total Guards: {total_guards}"
            )

    # ==================================================
    # TAB 2 - ADD GUARD
    # ==================================================

    with tab2:
        sub_header("Add New Guard","","➕")

        next_employee_id = get_next_employee_id()

        st.info(
            f"Next Employee ID: **{next_employee_id}**"
        )

        # ----------------------------------------------
        # AVAILABLE SECURITY GUARD USERS
        # ----------------------------------------------

        available_users = get_available_guard_users()

        user_options = {
            "No User Account": None
        }

        for user in available_users:

            user_options[
                f"{user.username} (ID: {user.id})"
            ] = user.id

        # ----------------------------------------------
        # ADD GUARD FORM
        # ----------------------------------------------

        with st.form(
            "create_guard_form",
            clear_on_submit=True
        ):

            # ==========================================
            # PERSONAL INFORMATION
            # ==========================================

            st.markdown(
                "### 👤 Personal Information"
            )

            col1, col2 = st.columns(2)

            with col1:

                name = text_input(
                    "Full Name *",
                    placeholder="Enter full name"
                )

                phone = text_input(
                    "Phone Number *",
                    max_chars=10,
                    placeholder="Enter 10 digit phone number"
                )

                text_input(
                    "Employee ID",
                    value=next_employee_id,
                    disabled=True
                )

            with col2:

                email = text_input(
                    "Email",
                    placeholder="Enter email address"
                )

                aadhaar_number = text_input(
                    "Aadhaar Number *",
                    type="password",
                    max_chars=12,
                    placeholder="Enter 12 digit Aadhaar number"
                )

                emergency_contact = text_input(
                    "Emergency Contact",
                    max_chars=10,
                    placeholder="Enter emergency contact number"
                )

            # ==========================================
            # ADDRESS
            # ==========================================

            st.markdown(
                "### 🏠 Address"
            )

            address = text_area(
                "Full Address",
                placeholder="Enter complete residential address"
            )

            pincode = text_input(
                "PIN Code *",
                max_chars=6,
                placeholder="Enter 6 digit PIN code"
            )

            # ==========================================
            # EMPLOYMENT INFORMATION
            # ==========================================

            st.markdown(
                "### 💼 Employment Information"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                joining_date = date_input(
                    "Joining Date *",
                    value=date.today()
                )

            with col2:

                monthly_salary = number_input(
                    "Monthly Salary (₹) *",
                    min_value=0.0,
                    value=0.0,
                    step=500.0,
                    format="%.2f",
                    help=(
                        "Monthly salary paid to this guard"
                    )
                )

            with col3:

                status = select_box(
                    "Status",
                    [
                        "Active",
                        "Inactive"
                    ]
                )

            # ==========================================
            # USER ACCOUNT
            # ==========================================

            st.markdown(
                "### 🔐 Login Account"
            )

            selected_user_label = select_box(
                "Link Security Guard User Account",
                list(user_options.keys())
            )

            user_id = user_options[
                selected_user_label
            ]

            if not available_users:

                st.info(
                    "No available Security Guard user "
                    "accounts found. You can still create "
                    "a guard without a login account."
                )

            # ==========================================
            # PHOTO
            # ==========================================

            st.markdown(
                "### 📷 Guard Photo"
            )

            photo = st.file_uploader(
                "Upload Guard Photo",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp"
                ]
            )

            if photo:

                st.image(
                    photo,
                    caption="Photo Preview",
                    width=180
                )

            st.divider()

            submitted = st.form_submit_button(
                "➕ Create Guard",
                width="stretch",
                type="primary"
            )

        # ==============================================
        # PROCESS CREATE FORM
        # ==============================================

        if submitted:

            if not name.strip():

                st.error(
                    "Full name is required."
                )

                return

            valid, message = validate_phone(phone)

            if not valid:

                st.error(message)

                return

            valid, message = validate_pincode(
                pincode
            )

            if not valid:

                st.error(message)

                return

            valid, message = validate_aadhaar(
                aadhaar_number
            )

            if not valid:

                st.error(message)

                return

            if monthly_salary < 0:

                st.error(
                    "Monthly salary cannot be negative."
                )

                return

            success, message = create_guard(

                name=name,

                phone=phone,

                email=email,

                aadhaar_number=aadhaar_number,

                address=address,

                pincode=pincode,

                emergency_contact=emergency_contact,

                joining_date=joining_date,

                monthly_salary=monthly_salary,

                status=status,

                user_id=user_id,

                photo=photo
            )

            if success:

                st.success(message)

                st.rerun()

            else:

                st.error(message)

    # ==================================================
    # TAB 3 - MANAGE GUARD
    # ==================================================

    with tab3:

        #st.subheader("⚙️ Manage Guard")

        st.html(
                            """
                            <div class="dashboard-section-title">
                                ⚙️ Manage Guard
                            </div>
                            """
                        )

        guards = get_all_guards()

        if not guards:

            st.info(
                "No guards available to manage."
            )

        else:

            # ----------------------------------------------
            # GUARD SELECTOR
            # ----------------------------------------------

            guard_options = {}

            for guard in guards:

                guard_options[
                    f"{guard.employee_id} - {guard.name}"
                ] = guard.id

            selected_guard_label = select_box(
                "Select Guard",
                list(guard_options.keys()),
                key="manage_guard_selector"
            )

            selected_guard_id = guard_options[
                selected_guard_label
            ]

            guard = get_guard_by_id(
                selected_guard_id
            )

            if guard:

                # ==========================================
                # PROFILE HEADER
                # ==========================================

                col1, col2 = st.columns([
                    1,
                    3
                ])

                with col1:

                    photo_path = get_guard_photo_path(
                        guard.photo_path
                    )

                    if photo_path:

                        st.image(
                            photo_path,
                            caption=guard.name,
                            width=180
                        )

                    else:

                        st.info(
                            "No photo available."
                        )

                with col2:

                    st.markdown(
                        f"### {guard.name}"
                    )

                    st.write(
                        f"**Employee ID:** "
                        f"{guard.employee_id}"
                    )

                    st.write(
                        f"**Phone:** "
                        f"{guard.phone or '-'}"
                    )

                    st.write(
                        f"**Status:** "
                        f"{guard.status}"
                    )

                    st.write(
                        f"**Aadhaar:** "
                        f"{mask_aadhaar(guard.aadhaar_number)}"
                    )

                # ==========================================
                # GUARD METRICS
                # ==========================================

                st.divider()

                salary = float(
                    getattr(
                        guard,
                        "monthly_salary",
                        0
                    ) or 0
                )

                metric_col1, metric_col2, metric_col3 = st.columns(3)

                with metric_col1:

                    st.metric(
                        "💰 Monthly Salary",
                        f"₹ {salary:,.2f}"
                    )

                with metric_col2:

                    st.metric(
                        "📅 Joining Date",
                        str(
                            guard.joining_date
                            or "-"
                        )
                    )

                with metric_col3:

                    assignments = get_guard_sites(
                        guard.id
                    )

                    st.metric(
                        "🏢 Assigned Sites",
                        len(assignments)
                    )

                # ==========================================
                # SITE ASSIGNMENT
                # ==========================================

                show_guard_site_assignment(guard)

                st.divider()

                # ==========================================
                # EDIT GUARD FORM
                # ==========================================

                st.markdown(
                    "### ✏️ Edit Guard Profile"
                )

                with st.form(
                    f"edit_guard_form_{guard.id}"
                ):

                    # --------------------------------------
                    # PERSONAL INFORMATION
                    # --------------------------------------

                    st.markdown(
                        "#### 👤 Personal Information"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        edit_name = text_input(
                            "Full Name *",
                            value=guard.name or ""
                        )

                        edit_phone = text_input(
                            "Phone Number *",
                            value=guard.phone or "",
                            max_chars=10
                        )

                        text_input(
                            "Employee ID",
                            value=guard.employee_id,
                            disabled=True
                        )

                    with col2:

                        edit_email = text_input(
                            "Email",
                            value=guard.email or ""
                        )

                        edit_aadhaar = text_input(
                            "Aadhaar Number *",
                            value=guard.aadhaar_number or "",
                            type="password",
                            max_chars=12
                        )

                        edit_emergency_contact = text_input(
                            "Emergency Contact",
                            value=(
                                guard.emergency_contact
                                or ""
                            ),
                            max_chars=10
                        )

                    # --------------------------------------
                    # ADDRESS
                    # --------------------------------------

                    st.markdown(
                        "#### 🏠 Address"
                    )

                    edit_address = text_area(
                        "Full Address",
                        value=guard.address or ""
                    )

                    edit_pincode = text_input(
                        "PIN Code *",
                        value=guard.pincode or "",
                        max_chars=6
                    )

                    # --------------------------------------
                    # EMPLOYMENT
                    # --------------------------------------

                    st.markdown(
                        "#### 💼 Employment Information"
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        edit_joining_date = date_input(
                            "Joining Date *",
                            value=guard.joining_date
                        )

                    with col2:

                        edit_monthly_salary = number_input(
                            "Monthly Salary (₹) *",
                            min_value=0.0,
                            value=float(
                                getattr(
                                    guard,
                                    "monthly_salary",
                                    0
                                ) or 0
                            ),
                            step=500.0,
                            format="%.2f",
                            key=(
                                f"edit_monthly_salary_"
                                f"{guard.id}"
                            ),
                            help=(
                                "Monthly salary paid to "
                                "this guard"
                            )
                        )

                    with col3:

                        status_options = [
                            "Active",
                            "Inactive"
                        ]

                        status_index = (
                            status_options.index(
                                guard.status
                            )
                            if guard.status in status_options
                            else 0
                        )

                        edit_status = select_box(
                            "Status",
                            status_options,
                            index=status_index
                        )

                    # --------------------------------------
                    # PHOTO
                    # --------------------------------------

                    st.markdown(
                        "#### 📷 Change Photo"
                    )

                    edit_photo = st.file_uploader(
                        "Upload New Photo",
                        type=[
                            "jpg",
                            "jpeg",
                            "png",
                            "webp"
                        ],
                        key=f"photo_{guard.id}"
                    )

                    if edit_photo:

                        st.image(
                            edit_photo,
                            caption="New Photo Preview",
                            width=180
                        )

                    st.divider()

                    update_submitted = (
                        st.form_submit_button(
                            "💾 Update Guard",
                            width="stretch",
                            type="primary"
                        )
                    )

                # ==========================================
                # PROCESS UPDATE FORM
                # ==========================================

                if update_submitted:

                    if not edit_name.strip():

                        st.error(
                            "Full name is required."
                        )

                        return

                    valid, message = validate_phone(
                        edit_phone
                    )

                    if not valid:

                        st.error(message)

                        return

                    valid, message = validate_pincode(
                        edit_pincode
                    )

                    if not valid:

                        st.error(message)

                        return

                    valid, message = validate_aadhaar(
                        edit_aadhaar
                    )

                    if not valid:

                        st.error(message)

                        return

                    if edit_monthly_salary < 0:

                        st.error(
                            "Monthly salary cannot be negative."
                        )

                        return

                    success, message = update_guard(

                        guard_id=guard.id,

                        name=edit_name,

                        phone=edit_phone,

                        email=edit_email,

                        aadhaar_number=edit_aadhaar,

                        address=edit_address,

                        pincode=edit_pincode,

                        emergency_contact=edit_emergency_contact,

                        joining_date=edit_joining_date,

                        monthly_salary=edit_monthly_salary,

                        status=edit_status,

                        user_id=guard.user_id,

                        photo=edit_photo
                    )

                    if success:

                        st.success(message)

                        st.rerun()

                    else:

                        st.error(message)


# ==================================================
# GUARD SITE ASSIGNMENT
# ==================================================

def show_guard_site_assignment(guard):

    st.divider()

    st.subheader("🏢 Assigned Sites")

    assignments = get_guard_sites(guard.id)

    # ==============================================
    # GET ACTIVE SITES
    # ==============================================

    sites = get_all_sites()

    active_sites = [
        site
        for site in sites
        if site.status == "Active"
    ]

    # ----------------------------------------------
    # FILTER ALREADY ASSIGNED SITES
    # ----------------------------------------------

    assigned_site_ids = {
        assignment.site_id
        for assignment in assignments
    }

    available_sites = [
        site
        for site in active_sites
        if site.id not in assigned_site_ids
    ]

    # ==============================================
    # ASSIGN SITE
    # ==============================================

    if available_sites:

        site_options = {
            f"{site.site_code} - {site.name}": site.id
            for site in available_sites
        }

        selected_site_label = select_box(
            "Select Site",
            list(site_options.keys()),
            key=f"assign_site_{guard.id}"
        )

        if button(
            "➕ Assign Site",
            key=f"assign_site_button_{guard.id}",
            type="primary",
            width="stretch"
        ):

            try:

                assign_guard_to_site(
                    guard_id=guard.id,
                    site_id=site_options[
                        selected_site_label
                    ]
                )

                st.success(
                    "Site assigned successfully."
                )

                st.rerun()

            except Exception as e:

                st.error(str(e))

    else:

        st.info(
            "No additional active sites are available."
        )

    # ==============================================
    # DISPLAY ASSIGNED SITES
    # ==============================================

    if not assignments:

        st.info(
            "This guard is not assigned to any site."
        )

        return

    st.caption(
        f"Total Assigned Sites: {len(assignments)}"
    )

    for assignment in assignments:

        site = assignment.site

        col1, col2, col3 = st.columns(
            [3, 2, 1]
        )

        with col1:

            st.markdown(
                f"**🏢 {site.name}**"
            )

            st.caption(
                f"Site Code: {site.site_code}"
            )

        with col2:

            st.write(
                f"📍 {site.city or 'N/A'}"
            )

            st.caption(
                f"Assigned: "
                f"{assignment.assigned_date}"
            )

        with col3:

            if button(
                "❌ Unassign",
                key=f"guard_unassign_{assignment.id}",
                type="secondary",
                width="stretch"
            ):

                try:

                    unassign_guard_from_site(
                        assignment.id
                    )

                    st.success(
                        "Site unassigned successfully."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(str(e))