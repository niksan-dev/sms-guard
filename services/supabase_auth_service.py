import os

from dotenv import load_dotenv
from supabase import create_client, Client


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# GET SUPABASE CONFIGURATION
# =========================================================

ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "development"
).lower()


if ENVIRONMENT == "production":

    SUPABASE_URL = os.getenv(
        "SUPABASE_URL_PROD"
    )

    SUPABASE_SECRET_KEY = os.getenv(
        "SUPABASE_SECRET_KEY_PROD"
    )

else:

    SUPABASE_URL = os.getenv(
        "SUPABASE_URL_DEV"
    )

    SUPABASE_SECRET_KEY = os.getenv(
        "SUPABASE_SECRET_KEY_DEV"
    )


# =========================================================
# VALIDATE CONFIGURATION
# =========================================================

if not SUPABASE_URL:
    raise RuntimeError(
        f"SUPABASE_URL is not configured "
        f"for environment: {ENVIRONMENT}"
    )


if not SUPABASE_SECRET_KEY:
    raise RuntimeError(
        f"SUPABASE_SECRET_KEY is not configured "
        f"for environment: {ENVIRONMENT}"
    )


# =========================================================
# SUPABASE CLIENT
# =========================================================

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY
)


# =========================================================
# AUTHENTICATE USER
# =========================================================

def authenticate_with_supabase(
    email: str,
    password: str
):
    """
    Authenticate a user using Supabase Auth.

    Returns:
        Supabase Auth response on success.
        None on failure.
    """

    try:

        response = supabase.auth.sign_in_with_password(
            {
                "email": email.strip(),
                "password": password,
            }
        )

        return response

    except Exception as e:

        print(
            f"Supabase authentication failed: {e}"
        )

        return None