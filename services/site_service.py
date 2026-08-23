from database.connection import SessionLocal
from database.models import Site, User


# ==================================================
# GET DATABASE SESSION
# ==================================================

def get_db():

    return SessionLocal()


# ==================================================
# VALIDATE PHONE NUMBER
# ==================================================

def validate_phone(phone):

    if not phone:
        return True, ""

    phone = phone.strip()

    if not phone.isdigit():
        return False, "Contact phone must contain digits only."

    if len(phone) != 10:
        return False, "Contact phone must contain exactly 10 digits."

    return True, ""


# ==================================================
# VALIDATE PIN CODE
# ==================================================

def validate_pincode(pincode):

    if not pincode:
        return True, ""

    pincode = pincode.strip()

    if not pincode.isdigit():
        return False, "PIN code must contain digits only."

    if len(pincode) != 6:
        return False, "PIN code must contain exactly 6 digits."

    return True, ""


# ==================================================
# GET NEXT SITE CODE
# Example:
# SITE-0001
# SITE-0002
# ==================================================

def get_next_site_code():

    db = get_db()

    try:

        last_site = (
            db.query(Site)
            .order_by(Site.id.desc())
            .first()
        )

        if not last_site:

            return "SITE-0001"

        if not last_site.site_code:

            return f"SITE-{last_site.id + 1:04d}"

        try:

            last_number = int(
                last_site.site_code.split("-")[-1]
            )

            next_number = last_number + 1

            return f"SITE-{next_number:04d}"

        except (ValueError, IndexError):

            return f"SITE-{last_site.id + 1:04d}"

    finally:

        db.close()


# ==================================================
# GET ALL SITES
# ==================================================

def get_all_sites():

    db = get_db()

    try:

        return (
            db.query(Site)
            .order_by(Site.id.desc())
            .all()
        )

    finally:

        db.close()


# ==================================================
# GET SITE BY ID
# ==================================================

def get_site_by_id(site_id):

    db = get_db()

    try:

        return (
            db.query(Site)
            .filter(Site.id == site_id)
            .first()
        )

    finally:

        db.close()


# ==================================================
# GET CLIENT USERS
# ==================================================

def get_client_users():

    db = get_db()

    try:

        return (
            db.query(User)
            .filter(
                User.role == "Client"
            )
            .order_by(User.username.asc())
            .all()
        )

    finally:

        db.close()


# ==================================================
# CREATE SITE
# ==================================================

def create_site(
    name,
    client_id,
    contact_person,
    contact_phone,
    email,
    address,
    city,
    state,
    pincode,
    guards_required,
    guard_rate=0.0,
    status="Active"
):

    db = get_db()

    try:

        # ------------------------------------------
        # CLEAN VALUES
        # ------------------------------------------

        name = name.strip() if name else ""

        contact_person = (
            contact_person.strip()
            if contact_person
            else None
        )

        contact_phone = (
            contact_phone.strip()
            if contact_phone
            else None
        )

        email = (
            email.strip()
            if email
            else None
        )

        address = (
            address.strip()
            if address
            else None
        )

        city = (
            city.strip()
            if city
            else None
        )

        state = (
            state.strip()
            if state
            else None
        )

        pincode = (
            pincode.strip()
            if pincode
            else None
        )

        guard_rate = float(guard_rate) if guard_rate else 0.0

        # ------------------------------------------
        # VALIDATE SITE NAME
        # ------------------------------------------

        if not name:

            return False, "Site name is required."

        # ------------------------------------------
        # VALIDATE PHONE
        # ------------------------------------------

        valid, message = validate_phone(
            contact_phone
        )

        if not valid:

            return False, message

        # ------------------------------------------
        # VALIDATE PIN CODE
        # ------------------------------------------

        valid, message = validate_pincode(
            pincode
        )

        if not valid:

            return False, message

        # ------------------------------------------
        # VALIDATE GUARDS REQUIRED
        # ------------------------------------------

        try:

            guards_required = int(guards_required)

            if guards_required < 1:

                return (
                    False,
                    "At least 1 guard is required."
                )

        except (ValueError, TypeError):

            return (
                False,
                "Invalid number of guards required."
            )

        # ------------------------------------------
        # GENERATE SITE CODE
        # ------------------------------------------

        site_code = get_next_site_code()

        # ------------------------------------------
        # CREATE SITE
        # ------------------------------------------

        new_site = Site(

            site_code=site_code,

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

        db.add(new_site)

        db.commit()

        db.refresh(new_site)

        return (
            True,
            f"Site created successfully. Site Code: {site_code}"
        )

    except Exception as e:

        db.rollback()

        return False, str(e)

    finally:

        db.close()


# ==================================================
# UPDATE SITE
# ==================================================

def update_site(
    site_id,
    name,
    client_id,
    contact_person,
    contact_phone,
    email,
    address,
    city,
    state,
    pincode,
    guards_required,
    guard_rate,
    status
):

    db = get_db()

    try:

        site = (
            db.query(Site)
            .filter(Site.id == site_id)
            .first()
        )

        if not site:

            return False, "Site not found."

        # ------------------------------------------
        # CLEAN VALUES
        # ------------------------------------------

        name = name.strip() if name else ""

        contact_person = (
            contact_person.strip()
            if contact_person
            else None
        )

        contact_phone = (
            contact_phone.strip()
            if contact_phone
            else None
        )

        email = (
            email.strip()
            if email
            else None
        )

        address = (
            address.strip()
            if address
            else None
        )

        city = (
            city.strip()
            if city
            else None
        )

        state = (
            state.strip()
            if state
            else None
        )

        pincode = (
            pincode.strip()
            if pincode
            else None
        )

        # ------------------------------------------
        # VALIDATION
        # ------------------------------------------

        if not name:

            return False, "Site name is required."

        valid, message = validate_phone(
            contact_phone
        )

        if not valid:

            return False, message

        valid, message = validate_pincode(
            pincode
        )

        if not valid:

            return False, message

        try:

            guards_required = int(guards_required)

            if guards_required < 1:

                return (
                    False,
                    "At least 1 guard is required."
                )

        except (ValueError, TypeError):

            return (
                False,
                "Invalid number of guards required."
            )


        site.guard_rate = guard_rate

        # ------------------------------------------
        # UPDATE SITE
        # ------------------------------------------

        site.name = name

        site.client_id = client_id

        site.contact_person = contact_person

        site.contact_phone = contact_phone

        site.email = email

        site.address = address

        site.city = city

        site.state = state

        site.pincode = pincode

        site.guards_required = guards_required

        site.guard_rate = guard_rate

        site.status = status

        db.commit()

        db.refresh(site)

        return True, "Site updated successfully."

    except Exception as e:

        db.rollback()

        return False, str(e)

    finally:

        db.close()


# ==================================================
# DELETE SITE
# ==================================================

def delete_site(site_id):

    db = get_db()

    try:

        site = (
            db.query(Site)
            .filter(Site.id == site_id)
            .first()
        )

        if not site:

            return False, "Site not found."

        db.delete(site)

        db.commit()

        return True, "Site deleted successfully."

    except Exception as e:

        db.rollback()

        return False, str(e)

    finally:

        db.close()