import streamlit as st
import pandas as pd
from pathlib import Path

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
from components.submit_button import submit_button

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

from services.guard_document_service import (
    DOCUMENT_TYPES,
    get_guard_documents,
    get_guard_document,
    save_guard_document,
    delete_guard_document,
    get_guard_document_file,
    get_document_readiness,
    create_guard_documents_zip,
)

from services.guard_deployment_service import (
    generate_guard_deployment_pdf,
)



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

                    "Emergency Contact":
                        guard.emergency_contact or "",

                    "Monthly Salary (₹)":
                        monthly_salary,


                    "Joining Date":
                        guard.joining_date,

                    "Status":
                        guard.status or "",

                    "Documents":
                        len(get_guard_documents(guard.id)),

                    "Document Readiness":
                        (
                            f"{get_document_readiness(guard.id)[0]}/"
                            f"{get_document_readiness(guard.id)[1]}"
                        ),
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

                    df["Emergency Contact"]
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

            col1, col2,col3 = st.columns(3)

            with col1:

                name = text_input(
                    "Full Name *",
                    placeholder="Enter full name"
                )

               

                # text_input(
                #     "Employee ID",
                #     value=next_employee_id,
                #     disabled=True
                # )

            with col2:

                phone = text_input(
                    "Phone Number *",
                    max_chars=10,
                    placeholder="Enter 10 digit phone number"
                )

                # email = text_input(
                #     "Email",
                #     placeholder="Enter email address"
                # )

            with col3:

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

            st.info(
                "📄 Guard documents can be uploaded and managed from "
                "Manage Guard after the guard profile is created."
            )

            st.divider()

            submitted = submit_button(
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


            if monthly_salary < 0:

                st.error(
                    "Monthly salary cannot be negative."
                )

                return

            success, message = create_guard(

                name=name,

                phone=phone,

                email="",


                address=address,


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
                # DOCUMENTS
                # ==========================================

                show_guard_documents(guard)

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

                    col1, col2,col3 = st.columns(3)

                    with col1:

                        edit_name = text_input(
                            "Full Name *",
                            value=guard.name or ""
                        )

                        

                        # text_input(
                        #     "Employee ID",
                        #     value=guard.employee_id,
                        #     disabled=True
                        # )

                    with col2:

                        edit_phone = text_input(
                            "Phone Number *",
                            value=guard.phone or "",
                            max_chars=10
                        )

                        # edit_email = text_input(
                        #     "Email",
                        #     value=guard.email or ""
                        # )

                    with col3:
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
                        submit_button(
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


                    if edit_monthly_salary < 0:

                        st.error(
                            "Monthly salary cannot be negative."
                        )

                        return

                    success, message = update_guard(

                        guard_id=guard.id,

                        name=edit_name,

                        phone=edit_phone,

                        email="",


                        address=edit_address,


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
# GUARD DOCUMENTS
# ==================================================

def show_guard_documents(guard):

    st.divider()

    st.subheader("📄 Guard Documents")

    completed, total_required, uploaded_types = (
        get_document_readiness(guard.id)
    )

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        st.metric(
            "📄 Documents Uploaded",
            len(get_guard_documents(guard.id))
        )

    with metric_col2:
        st.metric(
            "✅ Required Documents",
            f"{completed}/{total_required}"
        )

    with metric_col3:
        missing = total_required - completed
        st.metric(
            "⚠️ Missing Required",
            missing
        )

    st.caption(
        "Upload the document file for each document type. "
        "Document number and expiry date are not required. "
        "Uploading the same type again replaces the previous file."
    )

    # ----------------------------------------------
    # UPLOAD / REPLACE DOCUMENT
    # ----------------------------------------------

    st.markdown("#### ➕ Upload / Replace Document")

    doc_type = select_box(
        "Document Type",
        DOCUMENT_TYPES,
        key=f"guard_document_type_{guard.id}"
    )

    existing = get_guard_document(
        guard.id,
        doc_type
    )

    # Document number and expiry date are intentionally not collected.
    # The uploaded document file itself is the source of record.
    document_number = ""
    expiry_date = None

    current_label = (
        f"Current file: **{existing.original_filename}**"
        if existing
        else "No file uploaded yet."
    )

    st.caption(current_label)

    uploaded_file = st.file_uploader(
        "Select Document",
        type=["pdf", "jpg", "jpeg", "png", "webp"],
        key=f"guard_document_file_{guard.id}_{doc_type}"
    )

    if uploaded_file:
        st.caption(
            f"Selected: {uploaded_file.name} "
            f"({uploaded_file.size / 1024:.1f} KB)"
        )

    if button(
        "💾 Save Document",
        key=f"save_guard_document_{guard.id}_{doc_type}",
        type="primary",
        width="stretch"
    ):
        success, message = save_guard_document(
            guard_id=guard.id,
            document_type=doc_type,
            document_number=document_number,
            uploaded_file=uploaded_file,
            expiry_date=expiry_date
        )

        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)

    # ----------------------------------------------
    # CURRENT DOCUMENTS
    # ----------------------------------------------

    documents = get_guard_documents(guard.id)

    if not documents:
        st.info(
            "No documents uploaded for this guard yet."
        )
        return

    st.markdown("#### 📋 Uploaded Documents")

    for document in documents:

        col1, col2, col3, col4 = st.columns(
            [3, 2, 2, 1]
        )

        with col1:
            st.markdown(
                f"**📄 {document.document_type}**"
            )
            st.caption(
                document.original_filename
            )

        with col2:
            st.write("Document uploaded")

        with col3:
            st.write(
                document.uploaded_at.strftime("%d %b %Y")
                if document.uploaded_at
                else "-"
            )

        with col4:
            file_path, file_record = (
                get_guard_document_file(document.id)
            )

            if file_path and file_path.exists():
                try:
                    file_bytes = file_path.read_bytes()

                    st.download_button(
                        "⬇️",
                        data=file_bytes,
                        file_name=document.original_filename,
                        mime=document.mime_type or "application/octet-stream",
                        key=f"download_guard_document_{document.id}",
                        help="Download document"
                    )
                except Exception:
                    st.caption("File error")
            else:
                st.caption("Missing")

            if button(
                "🗑️",
                key=f"delete_guard_document_{document.id}",
                type="secondary",
                width="content"
            ):
                success, message = delete_guard_document(
                    document.id
                )

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)


def mask_document_number(document_number, document_type=""):

    if not document_number:
        return ""

    value = str(document_number).replace(
        " ",
        ""
    )

    document_type = str(
        document_type or ""
    ).lower()

    if "aadhaar" in document_type and len(value) == 12:
        return f"XXXX XXXX {value[-4:]}"

    if "pan" in document_type and len(value) == 10:
        return f"XXXXX{value[-5:]}"

    if len(value) <= 4:
        return "X" * len(value)

    return (
        f"{'X' * (len(value) - 4)}"
        f"{value[-4:]}"
    )


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

        # ----------------------------------------------
        # GUARD HANDOVER / DOCUMENT PACKAGE
        # ----------------------------------------------

        action_col1, action_col2 = st.columns(2)

        with action_col1:
            if st.button(
                "📄 Guard Details PDF",
                key=f"guard_details_pdf_{assignment.id}",
                width="stretch"
            ):
                try:
                    pdf_path = generate_guard_deployment_pdf(
                        guard_id=guard.id,
                        site_id=site.id
                    )

                    st.session_state[
                        f"guard_pdf_{assignment.id}"
                    ] = str(pdf_path)

                except Exception as e:
                    st.error(
                        f"Could not generate PDF: {e}"
                    )

            pdf_path_value = st.session_state.get(
                f"guard_pdf_{assignment.id}"
            )

            if pdf_path_value:
                pdf_path = Path(pdf_path_value)
                if pdf_path.exists():
                    st.download_button(
                        "⬇️ Download Guard Details",
                        data=pdf_path.read_bytes(),
                        file_name=pdf_path.name,
                        mime="application/pdf",
                        key=f"download_guard_details_{assignment.id}",
                        width="stretch"
                    )

        with action_col2:
            if st.button(
                "📦 Prepare Documents ZIP",
                key=f"guard_docs_zip_{assignment.id}",
                width="stretch"
            ):
                try:
                    zip_path = create_guard_documents_zip(
                        guard.id
                    )
                    st.session_state[
                        f"guard_zip_{assignment.id}"
                    ] = str(zip_path)
                except Exception as e:
                    st.error(
                        f"Could not prepare documents: {e}"
                    )

            zip_path_value = st.session_state.get(
                f"guard_zip_{assignment.id}"
            )

            if zip_path_value:
                zip_path = Path(zip_path_value)
                if zip_path.exists():
                    st.download_button(
                        "⬇️ Download All Documents",
                        data=zip_path.read_bytes(),
                        file_name=zip_path.name,
                        mime="application/zip",
                        key=f"download_guard_docs_{assignment.id}",
                        width="stretch"
                    )