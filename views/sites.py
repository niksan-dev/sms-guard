import streamlit as st
import pandas as pd

from services.site_service import (
    get_all_sites,
    get_site_by_id,
    get_client_users,
    create_site,
    update_site,
    delete_site,
    get_next_site_code
)

from services.site_guard_assignment_service import (
    assign_guard_to_site,
    get_site_guards,
    unassign_guard_from_site
)

from services.guard_service import get_all_guards

from components.page_header import page_header
from components.sub_header import sub_header
from components.text_input import text_input
from components.number_input import number_input
from components.select_box import select_box
from components.text_area import text_area
from components.search_box import search_box
from components.button import button
# ==================================================
# HELPER FUNCTIONS
# ==================================================

def get_client_name(client_id, clients):

    if not client_id:
        return "No Client Assigned"

    for client in clients:
        if client.id == client_id:
            return client.username

    return "Unknown Client"


def validate_phone_input(phone):

    if not phone:
        return True, ""

    phone = phone.strip()

    if not phone.isdigit():
        return False, "Phone number must contain digits only."

    if len(phone) != 10:
        return False, "Phone number must be exactly 10 digits."

    return True, ""


def validate_pincode_input(pincode):

    if not pincode:
        return True, ""

    pincode = pincode.strip()

    if not pincode.isdigit():
        return False, "PIN code must contain digits only."

    if len(pincode) != 6:
        return False, "PIN code must be exactly 6 digits."

    return True, ""


def get_site_monthly_amount(site):

    guards_required = int(site.guards_required or 0)
    guard_rate = float(site.guard_rate or 0)

    return guards_required * guard_rate


# ==================================================
# MAIN SITE MANAGEMENT PAGE
# ==================================================

def show_sites():

    # ----------------------------------------------
    # PAGE HEADER
    # ----------------------------------------------

    page_header("Site Management",
                "Manage client sites, security requirements and site information.",
                "🏢")
    
    # ----------------------------------------------
    # TABS
    # ----------------------------------------------

    tab_all, tab_add, tab_manage = st.tabs([
        "📋 All Sites",
        "➕ Add Site",
        "⚙️ Manage Site"
    ])

    # ==================================================
    # TAB 1 - ALL SITES
    # ==================================================

    with tab_all:

        
        sub_header("All Sites","","📋")

        sites = get_all_sites()
        clients = get_client_users()

        if not sites:

            st.info("No sites found. Add your first site.")

        else:

            # ------------------------------------------
            # SEARCH
            # ------------------------------------------

            search = search_box(
                "🔍 Search Site",
                placeholder="Search by site code, name, client, city or status...",
                key="site_search"
            )

            # ------------------------------------------
            # PREPARE DATA
            # ------------------------------------------

            site_data = []

            for current_site in sites:

                client_name = get_client_name(
                    current_site.client_id,
                    clients
                )

                monthly_amount = get_site_monthly_amount(
                    current_site
                )

                site_data.append({
                    "Site ID": current_site.id,
                    "Site Code": current_site.site_code or "",
                    "Site Name": current_site.name or "",
                    "Client": client_name,
                    "Contact Person": current_site.contact_person or "",
                    "Phone": current_site.contact_phone or "",
                    "City": current_site.city or "",
                    "State": current_site.state or "",
                    "Guards Required": int(
                        current_site.guards_required or 0
                    ),
                    "Guard Rate (₹)": float(
                        current_site.guard_rate or 0
                    ),
                    "Estimated Monthly Amount (₹)": monthly_amount,
                    "Status": current_site.status or ""
                })

            df = pd.DataFrame(site_data)

            # ------------------------------------------
            # SEARCH FILTER
            # ------------------------------------------

            filtered_df = df.copy()

            if search:

                search_text = search.lower().strip()

                mask = (
                    filtered_df["Site Code"]
                    .astype(str)
                    .str.lower()
                    .str.contains(search_text, na=False)
                    |
                    filtered_df["Site Name"]
                    .astype(str)
                    .str.lower()
                    .str.contains(search_text, na=False)
                    |
                    filtered_df["Client"]
                    .astype(str)
                    .str.lower()
                    .str.contains(search_text, na=False)
                    |
                    filtered_df["City"]
                    .astype(str)
                    .str.lower()
                    .str.contains(search_text, na=False)
                    |
                    filtered_df["Status"]
                    .astype(str)
                    .str.lower()
                    .str.contains(search_text, na=False)
                )

                filtered_df = filtered_df[mask]

            # ------------------------------------------
            # NO SEARCH RESULTS
            # ------------------------------------------

            if filtered_df.empty:

                st.warning("No sites found matching your search.")

            else:

                # --------------------------------------
                # AUTO SELECT SEARCH RESULT
                # --------------------------------------

                if len(filtered_df) == 1:

                    only_site_id = int(
                        filtered_df.iloc[0]["Site ID"]
                    )

                    st.session_state[
                        "selected_site_metrics_id"
                    ] = only_site_id

                # --------------------------------------
                # INITIAL SELECTED SITE
                # --------------------------------------

                available_site_ids = (
                    filtered_df["Site ID"]
                    .astype(int)
                    .tolist()
                )

                if (
                    "selected_site_metrics_id"
                    not in st.session_state
                ):
                    st.session_state[
                        "selected_site_metrics_id"
                    ] = available_site_ids[0]

                # If selected site is not in filtered results
                if (
                    st.session_state[
                        "selected_site_metrics_id"
                    ]
                    not in available_site_ids
                ):
                    st.session_state[
                        "selected_site_metrics_id"
                    ] = available_site_ids[0]

                # --------------------------------------
                # SITE METRIC SELECTOR
                # --------------------------------------

                site_labels = {}

                for _, row in filtered_df.iterrows():

                    label = (
                        f"{row['Site Code']} - "
                        f"{row['Site Name']}"
                    )

                    site_labels[label] = int(
                        row["Site ID"]
                    )

                current_selected_id = (
                    st.session_state[
                        "selected_site_metrics_id"
                    ]
                )

                current_index = 0

                label_list = list(site_labels.keys())

                for index, label in enumerate(label_list):

                    if site_labels[label] == current_selected_id:

                        current_index = index
                        break

                selected_site_label = select_box(
                    "📊 View Site Metrics",
                    options=label_list,
                    index=current_index,
                    key="site_metrics_selector"
                )

                selected_site_id = site_labels[
                    selected_site_label
                ]

                st.session_state[
                    "selected_site_metrics_id"
                ] = selected_site_id

                # --------------------------------------
                # GET SELECTED SITE
                # --------------------------------------

                selected_site = get_site_by_id(
                    selected_site_id
                )

                # --------------------------------------
                # SUMMARY METRICS
                # --------------------------------------

                if selected_site:

                    selected_site_name = f"Metrics for {selected_site.site_code} - {selected_site.name}"

                    sub_header(selected_site_name,"","📊")

                    guards_required = int(
                        selected_site.guards_required or 0
                    )

                    guard_rate = float(
                        selected_site.guard_rate or 0
                    )

                    monthly_amount = (
                        guards_required * guard_rate
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "👮 Guards Required",
                            guards_required
                        )

                    with col2:

                        st.metric(
                            "💰 Rate Per Guard",
                            f"₹ {guard_rate:,.2f}"
                        )

                    with col3:

                        st.metric(
                            "📅 Estimated Monthly Amount",
                            f"₹ {monthly_amount:,.2f}"
                        )

                st.divider()

                # --------------------------------------
                # DISPLAY TABLE
                # --------------------------------------

                display_df = filtered_df.drop(
                    columns=["Site ID"]
                )

                st.dataframe(
                    display_df,
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "Guard Rate (₹)": st.column_config.NumberColumn(
                            format="₹ %.2f"
                        ),
                        "Estimated Monthly Amount (₹)": (
                            st.column_config.NumberColumn(
                                format="₹ %.2f"
                            )
                        )
                    }
                )

    # ==================================================
    # TAB 2 - ADD SITE
    # ==================================================

    with tab_add:

        sub_header("Add New Site","","➕")

        st.info(
            f"Next Site Code: {get_next_site_code()}"
        )

        clients = get_client_users()

        if not clients:

            st.warning(
                "No Client users found. "
                "Please create a Client user first."
            )

        # ----------------------------------------------
        # CLIENT OPTIONS
        # ----------------------------------------------

        client_options = {
            "No Client Assigned": None
        }

        for client in clients:

            client_options[
                f"{client.username} ({client.email or 'No Email'})"
            ] = client.id

        with st.form(
            "add_site_form",
            clear_on_submit=True
        ):

            # ------------------------------------------
            # SITE INFORMATION
            # ------------------------------------------

            sub_header("Site Information","","🏢")

            col1, col2 = st.columns(2)

            with col1:

                name = text_input(
                    "Site Name *",
                    placeholder="Enter site name"
                )

            with col2:

                selected_client = select_box(
                    "Client",
                    options=list(client_options.keys())
                )

            # ------------------------------------------
            # CONTACT INFORMATION
            # ------------------------------------------

            sub_header("Contact Information","","📞")

            col1, col2, col3 = st.columns(3)

            with col1:

                contact_person = text_input(
                    "Contact Person",
                    placeholder="Enter contact person name"
                )

            with col2:

                contact_phone = text_input(
                    "Contact Phone",
                    max_chars=10,
                    placeholder="10 digit phone number"
                )

            with col3:

                email = text_input(
                    "Email",
                    placeholder="example@email.com"
                )

            # ------------------------------------------
            # ADDRESS
            # ------------------------------------------

            sub_header("Site Address","","📍")

            address = text_area(
                "Address",
                placeholder="Enter complete site address"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                city = text_input("City")

            with col2:

                state = text_input("State")

            with col3:

                pincode = text_input(
                    "PIN Code",
                    max_chars=6,
                    placeholder="6 digit PIN code"
                )

            # ------------------------------------------
            # SECURITY REQUIREMENTS
            # ------------------------------------------


            sub_header("Security Requirements","","🛡️")

            col1, col2, col3 = st.columns(3)

            with col1:

                guards_required = number_input(
                    "Number of Guards Required *",
                    min_value=1,
                    value=1,
                    step=1
                )

            with col2:

                guard_rate = number_input(
                    "Monthly Rate Per Guard (₹)",
                    min_value=0.0,
                    value=0.0,
                    step=1000.0,
                    format="%.2f",
                    help=(
                        "Monthly amount charged "
                        "for one guard at this site"
                    )
                )

            with col3:

                status = select_box(
                    "Status",
                    ["Active", "Inactive"]
                )

            st.divider()

            submitted = st.form_submit_button(
                "➕ Create Site",
                width="stretch",
                type="primary"
            )

            # ------------------------------------------
            # SUBMIT
            # ------------------------------------------

            if submitted:

                if not name.strip():

                    st.error("Site name is required.")
                    return

                valid, message = validate_phone_input(
                    contact_phone
                )

                if not valid:

                    st.error(message)
                    return

                valid, message = validate_pincode_input(
                    pincode
                )

                if not valid:

                    st.error(message)
                    return

                client_id = client_options.get(
                    selected_client
                )

                success, message = create_site(

                    name=name,

                    client_id=client_id,

                    contact_person=contact_person,

                    contact_phone=contact_phone,

                    email=email,

                    address=address,

                    city=city,

                    state=state,

                    pincode=pincode,

                    guards_required=guards_required,

                    guard_rate=guard_rate,

                    status=status
                )

                if success:

                    st.success(message)
                    st.rerun()

                else:

                    st.error(message)

    # ==================================================
    # TAB 3 - MANAGE SITE
    # ==================================================

    with tab_manage:


        sub_header("Manage Site","","⚙️")

        sites = get_all_sites()
        clients = get_client_users()

        if not sites:

            st.info(
                "No sites available to manage."
            )

        else:

            # ------------------------------------------
            # SITE SELECTOR
            # ------------------------------------------

            site_options = {}

            for site in sites:

                label = (
                    f"{site.site_code} - {site.name}"
                )

                site_options[label] = site.id

            selected_site_label = select_box(
                "Select Site",
                options=list(site_options.keys()),
                key="manage_site_selector"
            )

            selected_site_id = site_options.get(
                selected_site_label
            )

            site = get_site_by_id(
                selected_site_id
            )

            if site:

                st.divider()

                # --------------------------------------
                # SITE SUMMARY
                # --------------------------------------

                guards_required = int(
                    site.guards_required or 0
                )

                guard_rate = float(
                    site.guard_rate or 0
                )

                monthly_amount = (
                    guards_required * guard_rate
                )

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric(
                        "Site Code",
                        site.site_code
                    )

                with col2:

                    st.metric(
                        "Status",
                        site.status
                    )

                with col3:

                    st.metric(
                        "Guards Required",
                        guards_required
                    )

                with col4:

                    st.metric(
                        "Monthly Amount",
                        f"₹ {monthly_amount:,.2f}"
                    )

                # --------------------------------------
                # ASSIGNED GUARDS
                # --------------------------------------

                show_site_guard_assignment(site)

                st.divider()

                # --------------------------------------
                # CLIENT OPTIONS
                # --------------------------------------

                edit_client_options = {
                    "No Client Assigned": None
                }

                for client in clients:

                    edit_client_options[
                        f"{client.username} "
                        f"({client.email or 'No Email'})"
                    ] = client.id

                client_labels = list(
                    edit_client_options.keys()
                )

                current_client_index = 0

                for index, label in enumerate(
                    client_labels
                ):

                    if (
                        edit_client_options[label]
                        == site.client_id
                    ):

                        current_client_index = index
                        break

                # --------------------------------------
                # EDIT FORM
                # --------------------------------------

                with st.form(
                    f"edit_site_form_{site.id}"
                ):
                    

                    sub_header("Edit Site Information","","✏️")

                    # Basic Information

                    col1, col2 = st.columns(2)

                    with col1:

                        edit_name = text_input(
                            "Site Name *",
                            value=site.name or ""
                        )

                    with col2:

                        edit_selected_client = select_box(
                            "Client",
                            options=client_labels,
                            index=current_client_index
                        )

                    # Contact Information


                    sub_header("Contact Information","","📞")

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        edit_contact_person = text_input(
                            "Contact Person",
                            value=site.contact_person or ""
                        )

                    with col2:

                        edit_contact_phone = text_input(
                            "Contact Phone",
                            value=site.contact_phone or "",
                            max_chars=10
                        )

                    with col3:

                        edit_email = text_input(
                            "Email",
                            value=site.email or ""
                        )

                    # Address

                    sub_header("Site Address","","📍")

                    edit_address = text_area(
                        "Address",
                        value=site.address or ""
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        edit_city = text_input(
                            "City",
                            value=site.city or ""
                        )

                    with col2:

                        edit_state = text_input(
                            "State",
                            value=site.state or ""
                        )

                    with col3:

                        edit_pincode = text_input(
                            "PIN Code",
                            value=site.pincode or "",
                            max_chars=6
                        )

                    # Security Requirements


                    sub_header("Security Requirements","","🛡️")

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        edit_guards_required = number_input(
                            "Number of Guards Required *",
                            min_value=1,
                            value=max(
                                1,
                                int(
                                    site.guards_required or 1
                                )
                            ),
                            step=1
                        )

                    with col2:

                        edit_guard_rate = number_input(
                            "Monthly Rate Per Guard (₹)",
                            min_value=0.0,
                            value=float(
                                site.guard_rate or 0.0
                            ),
                            step=500.0,
                            format="%.2f"
                        )

                    with col3:

                        status_options = [
                            "Active",
                            "Inactive"
                        ]

                        current_status_index = (
                            status_options.index(site.status)
                            if site.status in status_options
                            else 0
                        )

                        edit_status = select_box(
                            "Status",
                            status_options,
                            index=current_status_index
                        )

                    st.divider()

                    update_submitted = (
                        st.form_submit_button(
                            "💾 Update Site",
                            width="stretch",
                            type="primary"
                        )
                    )

                    if update_submitted:

                        if not edit_name.strip():

                            st.error(
                                "Site name is required."
                            )

                            return

                        valid, message = validate_phone_input(
                            edit_contact_phone
                        )

                        if not valid:

                            st.error(message)
                            return

                        valid, message = validate_pincode_input(
                            edit_pincode
                        )

                        if not valid:

                            st.error(message)
                            return

                        edit_client_id = (
                            edit_client_options.get(
                                edit_selected_client
                            )
                        )

                        success, message = update_site(

                            site_id=site.id,

                            name=edit_name,

                            client_id=edit_client_id,

                            contact_person=edit_contact_person,

                            contact_phone=edit_contact_phone,

                            email=edit_email,

                            address=edit_address,

                            city=edit_city,

                            state=edit_state,

                            pincode=edit_pincode,

                            guards_required=edit_guards_required,

                            guard_rate=edit_guard_rate,

                            status=edit_status
                        )

                        if success:

                            st.success(message)
                            st.rerun()

                        else:

                            st.error(message)

                # --------------------------------------
                # DELETE SITE
                # --------------------------------------

                st.divider()

                with st.expander(
                    "🗑️ Delete Site"
                ):

                    st.warning(
                        "Deleting a site cannot be undone."
                    )

                    confirm_delete = st.checkbox(
                        (
                            "I understand that this action "
                            "cannot be undone."
                        ),
                        key=(
                            f"confirm_delete_site_{site.id}"
                        )
                    )

                    if button(
                        "🗑️ Delete Site Permanently",
                        key=f"delete_site_{site.id}",
                        type="primary",
                        width="stretch"
                    ):

                        if not confirm_delete:

                            st.error(
                                "Please confirm before "
                                "deleting the site."
                            )

                        else:

                            success, message = delete_site(
                                site.id
                            )

                            if success:

                                st.success(message)
                                st.rerun()

                            else:

                                st.error(message)


# ==================================================
# SITE GUARD ASSIGNMENT
# ==================================================

def show_site_guard_assignment(site):

    st.divider()

    sub_header("Assigned Guards","","👮")

    assignments = get_site_guards(site.id)

    assigned_count = len(assignments)
    required_count = int(site.guards_required or 0)

    st.caption(
        f"Assigned: {assigned_count} / {required_count}"
    )

    # ==============================================
    # ASSIGNED GUARD IDs
    # ==============================================

    assigned_guard_ids = {
        assignment.guard_id
        for assignment in assignments
    }

    # ==============================================
    # ASSIGN GUARD
    # ==============================================

    if assigned_count < required_count:

        guards = get_all_guards()

        # Active and not already assigned
        available_guards = [

            guard

            for guard in guards

            if (
                guard.status == "Active"
                and guard.id not in assigned_guard_ids
            )
        ]

        if available_guards:

            guard_options = {

                f"{guard.employee_id} - {guard.name}":
                guard.id

                for guard in available_guards
            }

            selected_guard_label = select_box(
                "Select Guard",
                list(guard_options.keys()),
                key=f"assign_guard_{site.id}"
            )

            if button(
                "➕ Assign Guard",
                key=f"assign_guard_button_{site.id}",
                type="primary",
                width="stretch"
            ):

                try:

                    assign_guard_to_site(

                        guard_id=guard_options[
                            selected_guard_label
                        ],

                        site_id=site.id
                    )

                    st.success(
                        "Guard assigned successfully."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(str(e))

        else:

            st.info(
                "No available active guards found."
            )

    else:

        st.warning(
            "Required number of guards has been assigned."
        )

    # ==============================================
    # DISPLAY ASSIGNED GUARDS
    # ==============================================

    if not assignments:

        st.info(
            "No guards assigned to this site yet."
        )

        return

    st.markdown("#### Currently Assigned Guards")

    for assignment in assignments:

        guard = assignment.guard

        col1, col2, col3 = st.columns(
            [3, 2, 1]
        )

        with col1:

            st.markdown(
                f"**👮 {guard.name}**"
            )

            st.caption(
                f"Employee ID: {guard.employee_id}"
            )

        with col2:

            st.write(
                f"📞 {guard.phone or 'N/A'}"
            )

            st.caption(
                f"Assigned: "
                f"{assignment.assigned_date}"
            )

        with col3:

            if button(
                "❌ Unassign",
                key=f"unassign_{assignment.id}",
                width="stretch"
            ):

                try:

                    unassign_guard_from_site(
                        assignment.id
                    )

                    st.success(
                        "Guard unassigned successfully."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(str(e))