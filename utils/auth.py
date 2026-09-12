import bcrypt

from database.connection import SessionLocal
from database.models import User
from utils.constants import UserRole

from services.supabase_auth_service import (
    authenticate_with_supabase,
)


# =========================================================
# PASSWORD HASHING
# =========================================================

def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")


def verify_password(
    plain_password: str,
    password_hash: str
) -> bool:

    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        password_hash.encode("utf-8")
    )


# =========================================================
# OLD DATABASE AUTHENTICATION
# =========================================================
#
# Kept temporarily for the existing Client / Guard
# authentication migration.
#
# DO NOT use this for the new Admin login.
#
# =========================================================

def authenticate_user(
    username: str,
    password: str
):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        # User does not exist
        if not user:
            return None

        # User is inactive
        if not user.is_active:
            return None

        # Wrong password
        if not verify_password(
            password,
            user.password_hash
        ):
            return None

        return user

    finally:
        db.close()


# =========================================================
# NEW SUPABASE AUTHENTICATION
# =========================================================

def authenticate_supabase_user(
    email: str,
    password: str
):
    """
    Authenticate a user through Supabase Auth.

    Supabase Auth is responsible for validating
    the email and password.

    After successful authentication, the Supabase
    user ID is used to find the corresponding
    application User record.

    Returns:
        SQLAlchemy User object on success.
        None on failure.
    """

    email = email.strip().lower()

    if not email or not password:
        return None

    # -----------------------------------------------------
    # Authenticate against Supabase Auth
    # -----------------------------------------------------

    response = authenticate_with_supabase(
        email=email,
        password=password,
    )

    if not response:
        return None

    # -----------------------------------------------------
    # Get Supabase Auth user
    # -----------------------------------------------------

    supabase_user = getattr(
        response,
        "user",
        None
    )

    if not supabase_user:
        return None

    supabase_user_id = getattr(
        supabase_user,
        "id",
        None
    )

    if not supabase_user_id:
        return None

    # -----------------------------------------------------
    # Find application user
    # -----------------------------------------------------

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.supabase_user_id == str(
                    supabase_user_id
                )
            )
            .first()
        )

        # Supabase user exists but has no
        # application profile.
        if not user:
            return None

        # -------------------------------------------------
        # Application account inactive
        # -------------------------------------------------

        if not user.is_active:
            return None

        return user

    finally:

        db.close()


# =========================================================
# CREATE APPLICATION USER
# =========================================================

def create_user(
    username: str,
    password: str,
    role: str = UserRole.CLIENT.value
):
    """
    Create a new application user.

    This is temporarily retained for the existing
    Client / Security Guard signup flow.

    Admin users should NOT be created through this
    function.
    """

    db = SessionLocal()

    try:

        # -------------------------------------------------
        # Check existing username
        # -------------------------------------------------

        existing_user = (
            db.query(User)
            .filter(
                User.username == username
            )
            .first()
        )

        if existing_user:
            return None, "Username already exists."

        # -------------------------------------------------
        # Create user
        # -------------------------------------------------

        new_user = User(
            username=username,
            password_hash=hash_password(password),
            role=role
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user, None

    except Exception as e:

        db.rollback()

        return None, str(e)

    finally:

        db.close()


# =========================================================
# DEFAULT SUPER ADMIN
# =========================================================
#
# IMPORTANT:
#
# The old hardcoded:
#
#     admin / admin123
#
# has intentionally been removed.
#
# Super Admin accounts are now created through
# Supabase Authentication and linked to the
# application's users table.
#
# =========================================================