from database.connection import SessionLocal
from database.models import User
from utils.constants import UserRole


SUPABASE_USER_ID = "7ea84326-30b6-425d-8069-eb595e3b318b"
ADMIN_EMAIL = "pravin.mokal@gmail.com"
ADMIN_USERNAME = "pravin.mokal"


def create_first_admin():

    db = SessionLocal()

    try:

        # -----------------------------------------------------
        # Check whether this Supabase user is already linked
        # -----------------------------------------------------

        existing = (
            db.query(User)
            .filter(
                User.supabase_user_id == SUPABASE_USER_ID
            )
            .first()
        )

        if existing:

            print("Admin is already linked.")
            print("Database User ID:", existing.id)
            print("Username:", existing.username)
            print("Email:", existing.email)
            print("Role:", existing.role)

            return

        # -----------------------------------------------------
        # Check email
        # -----------------------------------------------------

        existing_email = (
            db.query(User)
            .filter(
                User.email == ADMIN_EMAIL
            )
            .first()
        )

        if existing_email:

            existing_email.supabase_user_id = SUPABASE_USER_ID
            existing_email.role = UserRole.SUPER_ADMIN.value
            existing_email.is_active = True

            db.commit()
            db.refresh(existing_email)

            print("Existing user linked to Supabase Auth.")
            print("Database User ID:", existing_email.id)
            print("Username:", existing_email.username)
            print("Email:", existing_email.email)
            print("Role:", existing_email.role)

            return

        # -----------------------------------------------------
        # Create new application user
        # -----------------------------------------------------

        admin = User(
            supabase_user_id=SUPABASE_USER_ID,
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password_hash="SUPABASE_AUTH",
            role=UserRole.SUPER_ADMIN.value,
            is_active=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print()
        print("========================================")
        print("FIRST SUPER ADMIN CREATED")
        print("========================================")
        print("Database User ID:", admin.id)
        print("Supabase User ID:", admin.supabase_user_id)
        print("Username:", admin.username)
        print("Email:", admin.email)
        print("Role:", admin.role)
        print("========================================")

    except Exception as e:

        db.rollback()

        print()
        print("FAILED TO CREATE ADMIN")
        print(str(e))

    finally:

        db.close()


if __name__ == "__main__":
    create_first_admin()