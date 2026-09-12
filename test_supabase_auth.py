from utils.auth import authenticate_supabase_user


email = input("Admin email: ")
password = input("Admin password: ")


user = authenticate_supabase_user(
    email=email,
    password=password
)


if user:

    print()
    print("========================================")
    print("APPLICATION AUTHENTICATION SUCCESS")
    print("========================================")

    print("Database User ID:", user.id)
    print("Supabase User ID:", user.supabase_user_id)
    print("Username:", user.username)
    print("Email:", user.email)
    print("Role:", user.role)
    print("Active:", user.is_active)

    print("========================================")

else:

    print()
    print("========================================")
    print("APPLICATION AUTHENTICATION FAILED")
    print("========================================")