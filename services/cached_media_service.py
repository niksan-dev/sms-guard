import streamlit as st

from services.company_settings_service import get_company_settings
from services.supabase_storage_service import get_company_logo_url


# =========================================================
# CACHE SETTINGS
# =========================================================

# Signed URLs are valid for 1 hour in the current storage
# implementation. Keep the cached URL slightly shorter than
# that so an expired URL is never intentionally reused.
SIGNED_URL_TTL_SECONDS = 50 * 60


# =========================================================
# COMPANY LOGO
# =========================================================

@st.cache_data(
    ttl=SIGNED_URL_TTL_SECONDS,
    max_entries=32,
    show_spinner=False,
)
def get_cached_company_logo_url():
    """
    Return the company logo signed URL.

    The company settings DB lookup and Supabase signed-URL
    generation happen only on a cache miss. Normal Streamlit
    reruns/navigation clicks reuse the same URL.
    """
    try:
        settings = get_company_settings()

        if not settings:
            return None

        logo_path = getattr(
            settings,
            "logo_path",
            None,
        )

        if not logo_path:
            return None

        return get_company_logo_url(
            logo_path
        )

    except Exception:
        return None


# =========================================================
# GENERIC STORAGE URL CACHE
# =========================================================

@st.cache_data(
    ttl=SIGNED_URL_TTL_SECONDS,
    max_entries=256,
    show_spinner=False,
)
def get_cached_signed_url(
    bucket,
    path,
    expires_in=3600,
):
    """
    Cache any Supabase Storage signed URL.

    The cache key includes bucket/path/expires_in, so different
    files never share the wrong URL.
    """
    if not bucket or not path:
        return None

    try:
        from services.supabase_storage_service import get_signed_url

        return get_signed_url(
            bucket=bucket,
            path=path,
            expires_in=expires_in,
        )

    except (ImportError, AttributeError):
        if bucket == "company-assets":
            return get_company_logo_url(path)

        return None

    except Exception:
        return None


# =========================================================
# CACHE INVALIDATION
# =========================================================

def clear_media_cache():
    """
    Clear cached Storage URLs after an image is replaced
    or company settings are changed.
    """
    get_cached_company_logo_url.clear()
    get_cached_signed_url.clear()
