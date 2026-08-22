from database.connection import SessionLocal
from database.models import User
from utils.auth import hash_password


# ==================================================
# GET ALL USERS
# ==================================================

def get_all_users():

    db = SessionLocal()

    try:

        users = (
            db.query(User)
            .order_by(User.id.desc())
            .all()
        )

        return users

    finally:

        db.close()


# ==================================================
# GET USER BY ID
# ==================================================

def get_user_by_id(user_id: int):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        return user

    finally:

        db.close()


# ==================================================
# CREATE USER
# ==================================================

def create_user(
    username: str,
    email: str,
    phone: str,
    password: str,
    role: str
):

    db = SessionLocal()

    try:

        username = username.strip()
        email = email.strip() if email else None
        phone = phone.strip() if phone else None

        # ------------------------------------------
        # CHECK USERNAME
        # ------------------------------------------

        existing_username = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if existing_username:

            return False, "Username already exists."


        # ------------------------------------------
        # CHECK EMAIL
        # ------------------------------------------

        if email:

            existing_email = (
                db.query(User)
                .filter(User.email == email)
                .first()
            )

            if existing_email:

                return False, "Email already exists."


        # ------------------------------------------
        # CREATE USER
        # ------------------------------------------

        new_user = User(
            username=username,
            email=email,
            phone=phone,
            password_hash=hash_password(password),
            role=role,
            is_active=True
        )

        db.add(new_user)

        db.commit()

        db.refresh(new_user)

        return True, "User created successfully."

    except Exception as e:

        db.rollback()

        return False, str(e)

    finally:

        db.close()


# ==================================================
# UPDATE USER ROLE
# ==================================================

def update_user_role(
    user_id: int,
    role: str
):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:

            return False, "User not found."

        user.role = role

        db.commit()

        return True, "User role updated successfully."

    except Exception as e:

        db.rollback()

        return False, str(e)

    finally:

        db.close()


# ==================================================
# UPDATE USER STATUS
# ==================================================

def update_user_status(
    user_id: int,
    is_active: bool
):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:

            return False, "User not found."

        user.is_active = is_active

        db.commit()

        return True, "User status updated successfully."

    except Exception as e:

        db.rollback()

        return False, str(e)

    finally:

        db.close()


# ==================================================
# UPDATE USER PROFILE
# ==================================================

def update_user_profile(
    user_id: int,
    username: str,
    email: str,
    phone: str
):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            return False, "User not found."

        username = username.strip()
        email = email.strip() if email else None
        phone = phone.strip() if phone else None

        # Check duplicate username
        existing_username = (
            db.query(User)
            .filter(
                User.username == username,
                User.id != user_id
            )
            .first()
        )

        if existing_username:
            return False, "Username already exists."

        # Check duplicate email
        if email:

            existing_email = (
                db.query(User)
                .filter(
                    User.email == email,
                    User.id != user_id
                )
                .first()
            )

            if existing_email:
                return False, "Email already exists."

        # Update profile
        user.username = username
        user.email = email
        user.phone = phone

        db.commit()

        return True, "User profile updated successfully."

    except Exception as e:

        db.rollback()
        return False, str(e)

    finally:

        db.close()

# ==================================================
# RESET USER PASSWORD
# ==================================================

def reset_user_password(
    user_id: int,
    new_password: str
):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:

            return False, "User not found."

        if not new_password or len(new_password) < 6:

            return False, "Password must contain at least 6 characters."

        user.password_hash = hash_password(
            new_password
        )

        db.commit()

        return True, "Password reset successfully."

    except Exception as e:

        db.rollback()

        return False, str(e)

    finally:

        db.close()