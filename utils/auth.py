import bcrypt

from database.connection import SessionLocal
from database.models import User
from utils.constants import UserRole


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

        if not user:
            return None

        if not verify_password(
            password,
            user.password_hash
        ):
            return None

        return user

    finally:
        db.close()


def create_user(
    username: str,
    password: str,
    role: str = UserRole.CLIENT.value
):
    """
    Create a new user.
    """

    db = SessionLocal()

    try:

        # Check existing username
        existing_user = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if existing_user:
            return None, "Username already exists."

        # Create user
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


def create_default_super_admin():

    db = SessionLocal()

    try:

        existing_admin = (
            db.query(User)
            .filter(
                User.role == UserRole.SUPER_ADMIN.value
            )
            .first()
        )

        if existing_admin:
            return

        admin = User(
            username="admin",
            password_hash=hash_password("admin123"),
            role=UserRole.SUPER_ADMIN.value
        )

        db.add(admin)
        db.commit()

        print("Default Super Admin created.")

    finally:
        db.close()