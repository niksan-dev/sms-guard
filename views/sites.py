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


# ==================================================
# MAIN SITE MANAGEMENT PAGE
# ==================================================

def show_sites():

    # ----------------------------------------------
    # PAGE HEADER
    # ----------------------------------------------

    st.title("🏢 Site Management")

    st.caption(
        "Manage client sites, security requirements and site information."
    )

    st.divider()

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

        st.subheader("📋 All Sites")

        sites = get_all_sites()
        clients = get_client_users()

        if not sites:

            st.info("No sites found. Add your first site.")

        else:

            # ------------------------------------------
            # SEARCH
            # ------------------------------------------

            search = st.text_input(
                "🔍 Search Site",
                placeholder="Search by site code, name, city or status...",
                key="site_search"
            )

            # ------------------------------------------
            # PREPARE DATA
            # ------------------------------------------

            site_data = []

            for site in sites:

                client_name = get_client_name(
                    site.client_id,
                    clients
                )

                site_data.append({
                    "Site Code": site.site_code or "",
                    "Site Name": site.name or "",
                    "Client": client_name,
                    "Contact Person": site.contact_person or "",
                    "Phone": site.contact_phone or "",
                    "City": site.city or "",
                    "State": site.state or "",
                    "Guards Required": site.guards_required,
                    "Status": site.status or ""
                })

            df = pd.DataFrame(site_data)

            # ------------------------------------------
            # SEARCH FILTER
            # ------------------------------------------

            if search:

                search = search.lower()

                mask = (
                    df["Site Code"]
                    .astype(str)
                    .str.lower()
                    .str.contains(search, na=False)
                    |
                    df["Site Name"]
                    .astype(str)
                    .str.lower()
                    .str.contains(search, na=False)
                    |
                    df["Client"]
                    .astype(str)
                    .str.lower()
                    .str.contains(search, na=False)
                    |
                    df["City"]
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

            # ------------------------------------------
            # SUMMARY
            # ------------------------------------------

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Total Sites",
                    len(sites)
                )

            with col2:

                active_sites = sum(
                    1
                    for site in sites
                    if site.status == "Active"
                )

                st.metric(
                    "Active Sites",
                    active_sites
                )

            with col3:

                total_guards_required = sum(
                    site.guards_required or 0
                    for site in sites
                )

                st.metric(
                    "Guards Required",
                    total_guards_required
                )

            st.divider()

            # ------------------------------------------
            # TABLE
            # ------------------------------------------

            st.dataframe(
                df,
                width="stretch",
                hide_index=True
            )

    # ==================================================
    # TAB 2 - ADD SITE
    # ==================================================

    with tab_add:

        st.subheader("➕ Add New Site")

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
            # BASIC INFORMATION
            # ------------------------------------------

            st.markdown("### 🏢 Site Information")

            col1, col2 = st.columns(2)

            with col1:

                name = st.text_input(
                    "Site Name *",
                    placeholder="Enter site name"
                )

            with col2:

                selected_client = st.selectbox(
                    "Client",
                    options=list(client_options.keys())
                )

            # ------------------------------------------
            # CONTACT INFORMATION
            # ------------------------------------------

            st.markdown("### 📞 Contact Information")

            col1, col2, col3 = st.columns(3)

            with col1:

                contact_person = st.text_input(
                    "Contact Person",
                    placeholder="Enter contact person name"
                )

            with col2:

                contact_phone = st.text_input(
                    "Contact Phone",
                    max_chars=10,
                    placeholder="10 digit phone number"
                )

            with col3:

                email = st.text_input(
                    "Email",
                    placeholder="example@email.com"
                )

            # ------------------------------------------
            # ADDRESS
            # ------------------------------------------

            st.markdown("### 📍 Site Address")

            address = st.text_area(
                "Address",
                placeholder="Enter complete site address"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                city = st.text_input(
                    "City"
                )

            with col2:

                state = st.text_input(
                    "State"
                )

            with col3:

                pincode = st.text_input(
                    "PIN Code",
                    max_chars=6,
                    placeholder="6 digit PIN code"
                )

            # ------------------------------------------
            # SECURITY REQUIREMENTS
            # ------------------------------------------

            st.markdown("### 🛡️ Security Requirements")

            col1, col2 = st.columns(2)

            with col1:

                guards_required = st.number_input(
                    "Number of Guards Required *",
                    min_value=1,
                    value=1,
                    step=1
                )

            with col2:

                status = st.selectbox(
                    "Status",
                    [
                        "Active",
                        "Inactive"
                    ]
                )

            st.divider()

            submitted = st.form_submit_button(
                "➕ Create Site",
                width="stretch"
            )

            # ------------------------------------------
            # SUBMIT
            # ------------------------------------------

            if submitted:

                # Validate name

                if not name.strip():

                    st.error(
                        "Site name is required."
                    )

                    return

                # Validate phone

                valid, message = validate_phone_input(
                    contact_phone
                )

                if not valid:

                    st.error(message)

                    return

                # Validate PIN code

                valid, message = validate_pincode_input(
                    pincode
                )

                if not valid:

                    st.error(message)

                    return

                # Get selected client ID

                client_id = client_options.get(
                    selected_client
                )

                # Create site

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

        st.subheader("⚙️ Manage Site")

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

            selected_site_label = st.selectbox(
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
                # SITE DETAILS
                # --------------------------------------

                col1, col2, col3 = st.columns(3)

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
                        site.guards_required
                    )

                st.divider()

                # --------------------------------------
                # CLIENT OPTIONS
                # --------------------------------------

                edit_client_options = {
                    "No Client Assigned": None
                }

                for client in clients:

                    edit_client_options[
                        f"{client.username} ({client.email or 'No Email'})"
                    ] = client.id

                client_labels = list(
                    edit_client_options.keys()
                )

                # Find current client index

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

                    st.markdown(
                        "### ✏️ Edit Site Information"
                    )

                    # Basic

                    col1, col2 = st.columns(2)

                    with col1:

                        edit_name = st.text_input(
                            "Site Name *",
                            value=site.name or ""
                        )

                    with col2:

                        edit_selected_client = st.selectbox(
                            "Client",
                            options=client_labels,
                            index=current_client_index
                        )

                    # Contact

                    st.markdown(
                        "#### 📞 Contact Information"
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        edit_contact_person = st.text_input(
                            "Contact Person",
                            value=site.contact_person or ""
                        )

                    with col2:

                        edit_contact_phone = st.text_input(
                            "Contact Phone",
                            value=site.contact_phone or "",
                            max_chars=10
                        )

                    with col3:

                        edit_email = st.text_input(
                            "Email",
                            value=site.email or ""
                        )

                    # Address

                    st.markdown(
                        "#### 📍 Site Address"
                    )

                    edit_address = st.text_area(
                        "Address",
                        value=site.address or ""
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        edit_city = st.text_input(
                            "City",
                            value=site.city or ""
                        )

                    with col2:

                        edit_state = st.text_input(
                            "State",
                            value=site.state or ""
                        )

                    with col3:

                        edit_pincode = st.text_input(
                            "PIN Code",
                            value=site.pincode or "",
                            max_chars=6
                        )

                    # Requirements

                    st.markdown(
                        "#### 🛡️ Security Requirements"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        edit_guards_required = st.number_input(
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

                        status_options = [
                            "Active",
                            "Inactive"
                        ]

                        current_status_index = (
                            status_options.index(site.status)
                            if site.status in status_options
                            else 0
                        )

                        edit_status = st.selectbox(
                            "Status",
                            status_options,
                            index=current_status_index
                        )

                    st.divider()

                    update_submitted = (
                        st.form_submit_button(
                            "💾 Update Site",
                            width="stretch"
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
                        "I understand that this action cannot be undone.",
                        key=f"confirm_delete_site_{site.id}"
                    )

                    if st.button(
                        "🗑️ Delete Site Permanently",
                        key=f"delete_site_{site.id}",
                        type="primary"
                    ):

                        if not confirm_delete:

                            st.error(
                                "Please confirm before deleting the site."
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