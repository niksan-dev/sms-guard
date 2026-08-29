from database.connection import SessionLocal
from database.company_settings import CompanySettings


# ==================================================
# GET COMPANY SETTINGS
# ==================================================

def get_company_settings():

    db = SessionLocal()

    try:

        return (
            db.query(CompanySettings)
            .order_by(CompanySettings.id.asc())
            .first()
        )

    finally:

        db.close()


# ==================================================
# CREATE OR UPDATE COMPANY SETTINGS
# ==================================================

def save_company_settings(
    company_name,
    owner_name,
    address,
    city,
    state,
    pincode,
    phone,
    email,
    pan,
    gstin,
    invoice_prefix,
    bank_name,
    account_holder_name,
    account_number,
    ifsc_code,
    branch_name,
    logo_path=None
):

    db = SessionLocal()

    try:

        settings = (
            db.query(CompanySettings)
            .order_by(CompanySettings.id.asc())
            .first()
        )

        # ==========================================
        # CREATE COMPANY SETTINGS
        # ==========================================

        if settings is None:

            settings = CompanySettings(

                # Company information
                company_name=company_name,
                owner_name=owner_name,

                # Contact information
                phone=phone,
                email=email,

                # Address
                address=address,
                city=city,
                state=state,
                pincode=pincode,

                # Tax information
                pan_number=pan,
                gst_number=gstin,

                # Invoice settings
                invoice_prefix=invoice_prefix,

                # Bank details
                bank_name=bank_name,
                account_holder_name=account_holder_name,
                account_number=account_number,
                ifsc_code=ifsc_code,
                branch_name=branch_name,
                logo_path = logo_path
            )

            db.add(settings)


        # ==========================================
        # UPDATE COMPANY SETTINGS
        # ==========================================

        else:

            # Company information
            settings.company_name = company_name
            settings.owner_name = owner_name

            # Contact information
            settings.phone = phone
            settings.email = email

            # Address
            settings.address = address
            settings.city = city
            settings.state = state
            settings.pincode = pincode

            # Tax information
            settings.pan_number = pan
            settings.gst_number = gstin

            # Invoice settings
            settings.invoice_prefix = invoice_prefix

            # Bank details
            settings.bank_name = bank_name
            settings.account_holder_name = account_holder_name
            settings.account_number = account_number
            settings.ifsc_code = ifsc_code
            settings.branch_name = branch_name
            settings.logo_path = logo_path


        # ==========================================
        # SAVE
        # ==========================================

        db.commit()

        db.refresh(settings)

        return settings


    except Exception:

        db.rollback()

        raise


    finally:

        db.close()