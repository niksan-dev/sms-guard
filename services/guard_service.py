from pathlib import Path
from uuid import uuid4
from datetime import date

from database.connection import SessionLocal
from database.models import Guard, User
from utils.constants import UserRole


# ==================================================
# PROJECT PATHS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

GUARD_PHOTO_DIR = (
    PROJECT_ROOT
    / "uploads"
    / "guards"
)

GUARD_PHOTO_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# GET ALL GUARDS
# ==================================================

def get_all_guards(include_inactive=False):

    db = SessionLocal()

    try:

        query = db.query(Guard)

        if not include_inactive:
            query = query.filter(Guard.status == "Active")

        return (
            query
            .order_by(Guard.id.desc())
            .all()
        )

    finally:

        db.close()


# ==================================================
# GET GUARD BY ID
# ==================================================

def get_guard_by_id(guard_id: int):

    db = SessionLocal()

    try:

        return (
            db.query(Guard)
            .filter(Guard.id == guard_id)
            .first()
        )

    finally:

        db.close()


# ==================================================
# GENERATE NEXT EMPLOYEE ID
#
# SG-0001
# SG-0002
# SG-0003
# ...
# ==================================================

def generate_next_employee_id(db):

    employee_ids = (
        db.query(Guard.employee_id)
        .filter(
            Guard.employee_id.like("SG-%")
        )
        .all()
    )

    highest_number = 0

    for (employee_id,) in employee_ids:

        if not employee_id:
            continue

        try:

            # Example:
            # SG-0001 -> 0001 -> 1

            number_part = employee_id.replace(
                "SG-",
                "",
                1
            )

            number = int(number_part)

            if number > highest_number:

                highest_number = number

        except (
            ValueError,
            AttributeError
        ):

            # Ignore old/invalid employee IDs
            continue

    next_number = highest_number + 1

    return f"SG-{next_number:04d}"


# ==================================================
# GET NEXT EMPLOYEE ID
#
# Used only to preview the ID in the UI.
# The ID is generated again during save.
# ==================================================

def get_next_employee_id():

    db = SessionLocal()

    try:

        return generate_next_employee_id(db)

    finally:

        db.close()


# ==================================================
# GET AVAILABLE SECURITY GUARD USERS
#
# Only returns:
# - Role = Security Guard
# - Active users
# - Not already linked to another Guard profile
# ==================================================

def get_available_guard_users():

    db = SessionLocal()

    try:

        return (
            db.query(User)
            .outerjoin(
                Guard,
                Guard.user_id == User.id
            )
            .filter(
                User.role == UserRole.SECURITY_GUARD.value,
                User.is_active.is_(True),
                Guard.id.is_(None)
            )
            .order_by(User.username)
            .all()
        )

    finally:

        db.close()


# ==================================================
# VALIDATE PHONE
# ==================================================

def validate_phone(phone):

    if not phone:

        return (
            False,
            "Phone number is required."
        )

    phone = phone.strip()

    if not phone.isdigit():

        return (
            False,
            "Phone number must contain digits only."
        )

    if len(phone) != 10:

        return (
            False,
            "Phone number must contain exactly 10 digits."
        )

    return True, ""



# ==================================================
# SAVE GUARD PHOTO
# ==================================================

def save_guard_photo(
    uploaded_file,
    employee_id: str
):

    if not uploaded_file:

        return None

    try:

        original_name = uploaded_file.name

        extension = (
            Path(original_name)
            .suffix
            .lower()
        )

        allowed_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        }

        if extension not in allowed_extensions:

            raise ValueError(
                "Only JPG, JPEG, PNG and WEBP images are allowed."
            )

        # Example:
        # SG-0001_a1b2c3d4.jpg

        filename = (
            f"{employee_id}_"
            f"{uuid4().hex[:8]}"
            f"{extension}"
        )

        file_path = (
            GUARD_PHOTO_DIR
            / filename
        )

        with open(
            file_path,
            "wb"
        ) as file:

            file.write(
                uploaded_file.getbuffer()
            )

        # Store relative path in database
        return file_path.relative_to(PROJECT_ROOT).as_posix()

    except Exception as e:

        raise ValueError(
            f"Failed to save guard photo: {str(e)}"
        )


# ==================================================
# DELETE GUARD PHOTO
# ==================================================

def delete_guard_photo(photo_path: str):

    if not photo_path:

        return

    try:

        full_path = (
            PROJECT_ROOT
            / photo_path
        )

        if full_path.exists():

            full_path.unlink()

    except Exception as e:

        print(
            f"Failed to delete guard photo: {e}"
        )


# ==================================================
# GET GUARD PHOTO PATH
# ==================================================

def get_guard_photo_path(photo_path: str):

    if not photo_path:

        return None

    full_path = (
        PROJECT_ROOT
        / photo_path
    )

    if full_path.exists():

        return str(full_path)

    return None


# ==================================================
# CREATE GUARD
# ==================================================

def create_guard(
    name,
    phone,
    email,
    monthly_salary,
    address,
    emergency_contact,
    joining_date,
    status="Active",
    deactivation_date=None,
    user_id=None,
    photo=None
):

    db = SessionLocal()
    photo_path = None

    try:

        # ----------------------------------------------
        # CLEAN VALUES
        # ----------------------------------------------

        name = name.strip()

        phone = (
            phone.strip()
            if phone
            else ""
        )

        email = (
            email.strip().lower()
            if email
            else None
        )

        monthly_salary = float(monthly_salary or 0)

        address = (
            address.strip()
            if address
            else None
        )

        emergency_contact = (
            emergency_contact.strip()
            if emergency_contact
            else None
        )

        # ----------------------------------------------
        # VALIDATE NAME
        # ----------------------------------------------

        if not name:

            return (
                False,
                "Guard full name is required."
            )

        # ----------------------------------------------
        # VALIDATE PHONE
        # ----------------------------------------------

        valid_phone, phone_message = validate_phone(phone)

        if not valid_phone:

            return (
                False,
                phone_message
            )


        # ----------------------------------------------
        # VALIDATE MONTHLY SALARY
        # ----------------------------------------------

        if monthly_salary < 0:

            return (
                False,
                "Monthly salary cannot be negative."
            )

        # ----------------------------------------------
        # VALIDATE JOINING DATE
        # ----------------------------------------------

        if not joining_date:

            return (
                False,
                "Joining date is required."
            )


        # ----------------------------------------------
        # VALIDATE EMPLOYMENT STATUS / DEACTIVATION DATE
        # ----------------------------------------------

        if status not in ["Active", "Inactive"]:
            return (
                False,
                "Invalid guard status."
            )

        if status == "Active":
            deactivation_date = None

        else:
            if not deactivation_date:
                deactivation_date = date.today()

            if deactivation_date < joining_date:
                return (
                    False,
                    "Deactivation date cannot be before joining date."
                )

        # ----------------------------------------------
        # VALIDATE LINKED USER
        # ----------------------------------------------

        if user_id:

            user = (
                db.query(User)
                .filter(
                    User.id == user_id
                )
                .first()
            )

            if not user:

                return (
                    False,
                    "Selected user does not exist."
                )

            if (
                user.role
                != UserRole.SECURITY_GUARD.value
            ):

                return (
                    False,
                    "Only Security Guard users can be linked."
                )

            if not user.is_active:

                return (
                    False,
                    "Inactive users cannot be linked."
                )

            existing_link = (
                db.query(Guard)
                .filter(
                    Guard.user_id == user_id
                )
                .first()
            )

            if existing_link:

                return (
                    False,
                    "This user is already linked to another guard."
                )

        # ----------------------------------------------
        # GENERATE EMPLOYEE ID
        # ----------------------------------------------

        employee_id = generate_next_employee_id(db)

        # ----------------------------------------------
        # SAVE PHOTO
        # ----------------------------------------------

        if photo:

            photo_path = save_guard_photo(
                uploaded_file=photo,
                employee_id=employee_id
            )

        # ----------------------------------------------
        # CREATE GUARD
        # ----------------------------------------------

        new_guard = Guard(

            user_id=user_id,

            name=name,

            employee_id=employee_id,

            phone=phone,

            email=email,

            # NEW
            monthly_salary=monthly_salary,

            address=address,


            emergency_contact=emergency_contact,

            joining_date=joining_date,

            status=status,
            deactivation_date=deactivation_date,

            photo_path=photo_path
        )

        db.add(new_guard)

        db.commit()

        db.refresh(new_guard)

        return (
            True,
            f"Guard created successfully with Employee ID: {employee_id}"
        )

    except Exception as e:

        db.rollback()

        if photo_path:

            delete_guard_photo(
                photo_path
            )

        return (
            False,
            str(e)
        )

    finally:

        db.close()


# ==================================================
# UPDATE GUARD
#
# Employee ID is NOT changed automatically.
# ==================================================

def update_guard(
    guard_id,
    name,
    phone,
    email,
    monthly_salary,
    address,
    emergency_contact,
    joining_date,
    status,
    deactivation_date=None,
    user_id=None,
    photo=None
):

    db = SessionLocal()

    new_photo_path = None
    old_photo_path = None

    try:

        # ----------------------------------------------
        # GET GUARD
        # ----------------------------------------------

        guard = (
            db.query(Guard)
            .filter(
                Guard.id == guard_id
            )
            .first()
        )

        if not guard:

            return (
                False,
                "Guard not found."
            )

        # ----------------------------------------------
        # CLEAN VALUES
        # ----------------------------------------------

        name = name.strip()

        phone = (
            phone.strip()
            if phone
            else ""
        )

        email = (
            email.strip().lower()
            if email
            else None
        )

        monthly_salary = float(monthly_salary or 0)

        address = (
            address.strip()
            if address
            else None
        )

        emergency_contact = (
            emergency_contact.strip()
            if emergency_contact
            else None
        )

        # ----------------------------------------------
        # VALIDATE NAME
        # ----------------------------------------------

        if not name:

            return (
                False,
                "Guard full name is required."
            )

        # ----------------------------------------------
        # VALIDATE PHONE
        # ----------------------------------------------

        valid_phone, phone_message = validate_phone(phone)

        if not valid_phone:

            return (
                False,
                phone_message
            )


        # ----------------------------------------------
        # VALIDATE MONTHLY SALARY
        # ----------------------------------------------

        if monthly_salary < 0:

            return (
                False,
                "Monthly salary cannot be negative."
            )


        # ----------------------------------------------
        # VALIDATE EMPLOYMENT STATUS / DEACTIVATION DATE
        # ----------------------------------------------

        if status not in ["Active", "Inactive"]:
            return (
                False,
                "Invalid guard status."
            )

        if status == "Active":
            deactivation_date = None

        else:
            if not deactivation_date:
                deactivation_date = date.today()

            if deactivation_date < joining_date:
                return (
                    False,
                    "Deactivation date cannot be before joining date."
                )

        # ----------------------------------------------
        # VALIDATE LINKED USER
        # ----------------------------------------------

        if user_id:

            user = (
                db.query(User)
                .filter(
                    User.id == user_id
                )
                .first()
            )

            if not user:

                return (
                    False,
                    "Selected user does not exist."
                )

            if (
                user.role
                != UserRole.SECURITY_GUARD.value
            ):

                return (
                    False,
                    "Only Security Guard users can be linked."
                )

            if not user.is_active:

                return (
                    False,
                    "Inactive users cannot be linked."
                )

            duplicate_link = (
                db.query(Guard)
                .filter(
                    Guard.user_id == user_id,
                    Guard.id != guard_id
                )
                .first()
            )

            if duplicate_link:

                return (
                    False,
                    "This user is already linked to another guard."
                )

        # ----------------------------------------------
        # SAVE NEW PHOTO
        # ----------------------------------------------

        if photo:

            new_photo_path = save_guard_photo(
                uploaded_file=photo,
                employee_id=guard.employee_id
            )

            old_photo_path = guard.photo_path

        # ----------------------------------------------
        # UPDATE GUARD
        # ----------------------------------------------

        guard.user_id = user_id

        guard.name = name

        guard.phone = phone

        guard.email = email

        # NEW
        guard.monthly_salary = monthly_salary

        guard.address = address


        guard.emergency_contact = emergency_contact

        guard.joining_date = joining_date

        guard.status = status
        guard.deactivation_date = deactivation_date

        if new_photo_path:

            guard.photo_path = new_photo_path

        db.commit()

        db.refresh(guard)

        # ----------------------------------------------
        # DELETE OLD PHOTO
        # ----------------------------------------------

        if (
            new_photo_path
            and old_photo_path
        ):

            delete_guard_photo(
                old_photo_path
            )

        return (
            True,
            "Guard updated successfully."
        )

    except Exception as e:

        db.rollback()

        if new_photo_path:

            delete_guard_photo(
                new_photo_path
            )

        return (
            False,
            str(e)
        )

    finally:

        db.close()


# ==================================================
# UPDATE GUARD STATUS
# ==================================================

def update_guard_status(
    guard_id: int,
    status: str,
    deactivation_date=None
):

    db = SessionLocal()

    try:

        guard = (
            db.query(Guard)
            .filter(
                Guard.id == guard_id
            )
            .first()
        )

        if not guard:

            return (
                False,
                "Guard not found."
            )

        if status not in [
            "Active",
            "Inactive"
        ]:

            return (
                False,
                "Invalid guard status."
            )

        if status == "Active":
            guard.status = "Active"
            guard.deactivation_date = None

        else:
            if not deactivation_date:
                deactivation_date = date.today()

            if (
                guard.joining_date
                and deactivation_date < guard.joining_date
            ):
                return (
                    False,
                    "Deactivation date cannot be before joining date."
                )

            guard.status = "Inactive"
            guard.deactivation_date = deactivation_date

        db.commit()

        return (
            True,
            "Guard status updated successfully."
        )

    except Exception as e:

        db.rollback()

        return (
            False,
            str(e)
        )

    finally:

        db.close()



# ==================================================
# HISTORICAL GUARD DATE FILTER
# ==================================================

def get_guards_active_during(start_date, end_date=None):
    """
    Return guards whose employment period overlaps the
    requested date/date range.

    Current status is intentionally NOT used as the primary
    filter, so deactivated guards remain available for
    historical reports.
    """
    if not start_date:
        raise ValueError("Start date is required.")

    if not end_date:
        end_date = start_date

    if end_date < start_date:
        raise ValueError("End date cannot be before start date.")

    db = SessionLocal()

    try:
        return (
            db.query(Guard)
            .filter(
                Guard.joining_date <= end_date,
                (
                    (Guard.deactivation_date.is_(None))
                    | (Guard.deactivation_date >= start_date)
                )
            )
            .order_by(Guard.id.desc())
            .all()
        )
    finally:
        db.close()


def guard_was_active_on(guard, target_date):
    """
    Check whether a guard was active on a specific date.
    Useful for historical date-based screens.
    """
    if not guard or not target_date:
        return False

    if guard.joining_date and target_date < guard.joining_date:
        return False

    if (
        guard.deactivation_date
        and target_date > guard.deactivation_date
    ):
        return False

    return True
