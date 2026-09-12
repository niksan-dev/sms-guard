import os
import streamlit as st

from services.company_settings_service import (
    get_company_settings,
    save_company_settings
)

from services.supabase_storage_service import (
    upload_file,
)

from services.cached_media_service import (
    get_cached_company_logo_url,
    clear_media_cache,
)

from utils.validators import (
    validate_phone,
    validate_pincode,
    validate_pan,
    validate_gstin
)

from components.page_header import page_header
from components.sub_header import sub_header
from components.text_input import text_input
from components.number_input import number_input
from components.select_box import select_box
from components.text_area import text_area
from components.submit_button import submit_button


# ==================================================
# SAVE COMPANY LOGO
# ==================================================

def save_company_logo(uploaded_file):

    if uploaded_file is None:
        return None

    file_extension = os.path.splitext(
        uploaded_file.name
    )[1].lower()

    # Supabase Storage object path
    file_path = (
        f"company/company_logo{file_extension}"
    )

    upload_file(
        bucket="company-assets",
        path=file_path,
        file_data=uploaded_file.getbuffer(),
        content_type=uploaded_file.type,
        upsert=True
    )

    # Store only the Storage object path
    # in company_settings.logo_path
    return file_path


# ==================================================
# SAFE VALUE HELPER
# ==================================================

def get_value(settings, field_name, default=""):

    if settings is None:
        return default

    value = getattr(
        settings,
        field_name,
        default
    )

    return value if value is not None else default


# ==================================================
# COMPANY SETTINGS PAGE
# ==================================================

def show_company_settings():

    # ==============================================
    # ADMIN ACCESS CHECK
    # ==============================================

    user = st.session_state.get("user")

    if not user:

        st.error(
            "Please log in to access this page."
        )

        st.stop()

    role = user.get("role")

    if role not in ["Super Admin", "Admin"]:

        st.error(
            "⛔ You do not have permission to access Company Settings."
        )

        st.stop()


    # ==============================================
    # PAGE HEADER
    # ==============================================

    page_header(
        "Company Settings",
        "Manage company information, GST details,\nbank details and invoice settings.",
        "🏢"
    )


    # ==============================================
    # LOAD EXISTING SETTINGS
    # ==============================================

    try:

        settings = get_company_settings()

    except Exception as error:

        st.error(
            f"Unable to load company settings: {error}"
        )

        return


    # ==============================================
    # DISPLAY CURRENT LOGO
    # ==============================================

    current_logo = get_value(
        settings,
        "logo_path"
    )

    if current_logo:

        try:

            # Generate temporary signed URL
            logo_url = get_cached_company_logo_url()

            if logo_url:

                logo_col1, logo_col2 = st.columns(
                    [1, 5],
                    vertical_alignment="center"
                )

                with logo_col1:

                    st.image(
                        logo_url,
                        width=120
                    )

                with logo_col2:

                    st.success(
                        "Company logo configured."
                    )

        except Exception as error:

            st.warning(
                f"Unable to display company logo: {error}"
            )


    # ==============================================
    # COMPANY SETTINGS FORM
    # ==============================================

    with st.form(
        "company_settings_form"
    ):

        # ------------------------------------------
        # COMPANY INFORMATION
        # ------------------------------------------

        sub_header(
            " Company Information",
            "",
            "🏢"
        )

        col1, col2 = st.columns(2)

        with col1:

            company_name = text_input(
                "Company Name *",
                value=get_value(
                    settings,
                    "company_name"
                )
            )

        with col2:

            owner_name = text_input(
                "Owner / Authorized Person",
                value=get_value(
                    settings,
                    "owner_name"
                )
            )


        # ------------------------------------------
        # CONTACT INFORMATION
        # ------------------------------------------

        sub_header(
            "Contact Information",
            "",
            "📞"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            phone = text_input(
                "Phone Number",
                value=get_value(
                    settings,
                    "phone"
                ),
                max_chars=10
            )

        with col2:

            alternate_phone = text_input(
                "Alternate Contact Number",
                value=get_value(
                    settings,
                    "alternate_phone"
                ),
                max_chars=10
            )

        with col3:

            email = text_input(
                "Email Address",
                value=get_value(
                    settings,
                    "email"
                )
            )


        # ------------------------------------------
        # ADDRESS
        # ------------------------------------------

        sub_header(
            "Company Address",
            "",
            "📍"
        )

        address = text_area(
            "Address",
            value=get_value(
                settings,
                "address"
            ),
            height=100
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            city = text_input(
                "City",
                value=get_value(
                    settings,
                    "city"
                )
            )

        with col2:

            state = text_input(
                "State",
                value=get_value(
                    settings,
                    "state"
                )
            )

        with col3:

            pincode = text_input(
                "Pincode",
                value=get_value(
                    settings,
                    "pincode"
                ),
                max_chars=6
            )


        # ------------------------------------------
        # TAX INFORMATION
        # ------------------------------------------

        sub_header(
            "Tax Information",
            "",
            "🧾"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            pan = text_input(
                "PAN Number",
                value=get_value(
                    settings,
                    "pan_number"
                ),
                max_chars=10
            )

        with col2:

            gstin = text_input(
                "GSTIN",
                value=get_value(
                    settings,
                    "gst_number"
                ),
                max_chars=15
            )

        with col3:

            cgst_rate = number_input(
                "CGST Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(
                    get_value(
                        settings,
                        "cgst_rate",
                        9.0
                    )
                ),
                step=0.5,
                format="%.2f"
            )

        with col4:

            sgst_rate = number_input(
                "SGST Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(
                    get_value(
                        settings,
                        "sgst_rate",
                        9.0
                    )
                ),
                step=0.5,
                format="%.2f"
            )


        # ------------------------------------------
        # INVOICE SETTINGS
        # ------------------------------------------

        sub_header(
            "Invoice Settings",
            "",
            "📄"
        )

        invoice_prefix = text_input(
            "Invoice Prefix",
            value=get_value(
                settings,
                "invoice_prefix",
                "INV"
            )
        )

        st.caption(
            "Example: INV-202608-0001"
        )


        # ------------------------------------------
        # BANK DETAILS
        # ------------------------------------------

        sub_header(
            "Bank Details",
            "",
            "🏦"
        )

        col1, col2 = st.columns(2)

        with col1:

            bank_name = text_input(
                "Bank Name",
                value=get_value(
                    settings,
                    "bank_name"
                )
            )

        with col2:

            account_holder_name = text_input(
                "Account Holder Name",
                value=get_value(
                    settings,
                    "account_holder_name"
                )
            )


        col1, col2 = st.columns(2)

        with col1:

            account_number = text_input(
                "Account Number",
                value=get_value(
                    settings,
                    "account_number"
                ),
                type="password"
            )

        with col2:

            ifsc_code = text_input(
                "IFSC Code",
                value=get_value(
                    settings,
                    "ifsc_code"
                )
            )


        branch_name = text_input(
            "Branch Name",
            value=get_value(
                settings,
                "branch_name"
            )
        )


        # ------------------------------------------
        # COMPANY LOGO
        # ------------------------------------------

        sub_header(
            "Company Logo",
            "",
            "🖼️"
        )

        uploaded_logo = st.file_uploader(
            "Upload Company Logo",
            type=[
                "png",
                "jpg",
                "jpeg"
            ]
        )


        # ------------------------------------------
        # SAVE BUTTON
        # ------------------------------------------

        submitted = submit_button(
            "💾 Save Company Settings",
            width="stretch"
        )


    # ==============================================
    # FORM SUBMIT
    # ==============================================

    if not submitted:
        return


    # ----------------------------------------------
    # CLEAN VALUES
    # ----------------------------------------------

    company_name = company_name.strip()

    owner_name = owner_name.strip()

    address = address.strip()

    city = city.strip()

    state = state.strip()

    pincode = pincode.strip()

    phone = phone.strip()

    alternate_phone = alternate_phone.strip()

    email = email.strip()

    pan = pan.strip().upper()

    gstin = gstin.strip().upper()

    sgst_rate = float(sgst_rate)

    cgst_rate = float(cgst_rate)

    invoice_prefix = invoice_prefix.strip().upper()

    bank_name = bank_name.strip()

    account_holder_name = (
        account_holder_name.strip()
    )

    account_number = account_number.strip()

    ifsc_code = ifsc_code.strip().upper()

    branch_name = branch_name.strip()


    # ----------------------------------------------
    # REQUIRED VALIDATION
    # ----------------------------------------------

    if not company_name:

        st.error(
            "Company name is required."
        )

        return


    # ----------------------------------------------
    # PHONE VALIDATION
    # ----------------------------------------------

    if not validate_phone(phone):

        st.error(
            "Phone number must contain exactly 10 digits."
        )

        return


    # ----------------------------------------------
    # PINCODE VALIDATION
    # ----------------------------------------------

    if not validate_pincode(pincode):

        st.error(
            "Pincode must contain exactly 6 digits."
        )

        return


    # ----------------------------------------------
    # PAN VALIDATION
    # ----------------------------------------------

    if not validate_pan(pan):

        st.error(
            "Invalid PAN format. Example: ABCDE1234F"
        )

        return


    # ----------------------------------------------
    # GSTIN VALIDATION
    # ----------------------------------------------

    if not validate_gstin(gstin):

        st.error(
            "Invalid GSTIN format."
        )

        return


    # ==============================================
    # SAVE
    # ==============================================

    try:

        # ------------------------------------------
        # PRESERVE EXISTING LOGO
        # ------------------------------------------

        logo_path = get_value(
            settings,
            "logo_path",
            None
        )


        # ------------------------------------------
        # UPLOAD NEW LOGO
        # ------------------------------------------

        if uploaded_logo is not None:

            saved_logo_path = save_company_logo(
                uploaded_logo
            )

            if saved_logo_path:

                logo_path = saved_logo_path


        # ------------------------------------------
        # SAVE COMPANY SETTINGS
        # ------------------------------------------

        final_settings = save_company_settings(

            company_name=company_name,

            owner_name=owner_name,

            address=address,

            city=city,

            state=state,

            pincode=pincode,

            phone=phone,

            alternate_phone=alternate_phone,

            cgst_rate=cgst_rate,

            sgst_rate=sgst_rate,

            email=email,

            pan=pan,

            gstin=gstin,

            invoice_prefix=invoice_prefix,

            bank_name=bank_name,

            account_holder_name=(
                account_holder_name
            ),

            account_number=account_number,

            ifsc_code=ifsc_code,

            branch_name=branch_name,

            logo_path=logo_path
        )


        clear_media_cache()

        st.success(
            "✅ Company settings saved successfully."
        )

        st.rerun()


    except Exception as error:

        st.error(
            f"❌ Error saving company settings: {error}"
        )