"""Supabase Storage service.

Provides environment-aware access to Supabase Storage for:
- company assets
- guard photos
- guard documents
"""

from __future__ import annotations

import os
import uuid
from pathlib import PurePosixPath
from typing import BinaryIO

from supabase import create_client, Client


# ============================================================
# BUCKETS
# ============================================================

COMPANY_ASSETS_BUCKET = "company-assets"
GUARD_PHOTOS_BUCKET = "guard-photos"
GUARD_DOCUMENTS_BUCKET = "guard-documents"


# ============================================================
# STREAMLIT SECRET
# ============================================================

def _get_streamlit_secret(name: str) -> str | None:
    """Read a Streamlit secret safely."""
    try:
        import streamlit as st

        value = st.secrets.get(name)

        if value:
            return str(value).strip()

    except Exception:
        pass

    return None


# ============================================================
# ENVIRONMENT
# ============================================================

def _get_environment() -> str:
    """Return the current application environment."""

    value = os.getenv("ENVIRONMENT", "").strip().lower()

    if not value:
        value = (
            _get_streamlit_secret("ENVIRONMENT")
            or "development"
        ).strip().lower()

    if value not in {"development", "production"}:
        raise RuntimeError(
            "Invalid ENVIRONMENT. "
            "Expected 'development' or 'production'."
        )

    return value


# ============================================================
# CONFIGURATION
# ============================================================

def _get_config_value(base_name: str) -> str:
    """Get environment-specific configuration."""

    environment = _get_environment()

    suffix = (
        "PROD"
        if environment == "production"
        else "DEV"
    )

    variable_name = f"{base_name}_{suffix}"

    value = os.getenv(variable_name, "").strip()

    if not value:
        value = (
            _get_streamlit_secret(variable_name)
            or ""
        ).strip()

    if not value:
        raise RuntimeError(
            f"{variable_name} is not configured "
            f"for ENVIRONMENT={environment}."
        )

    return value


# ============================================================
# SUPABASE CLIENT
# ============================================================

def get_supabase_client() -> Client:
    """Create an environment-specific Supabase client."""

    supabase_url = _get_config_value("SUPABASE_URL")
    service_role_key = _get_config_value(
        "SUPABASE_SERVICE_ROLE_KEY"
    )

    return create_client(
        supabase_url,
        service_role_key,
    )


# ============================================================
# UPLOAD
# ============================================================

def upload_file(
    bucket: str,
    path: str,
    file_data: bytes | BinaryIO,
    content_type: str,
    *,
    upsert: bool = False,
) -> str:
    """Upload a file to Supabase Storage.

    Returns the Storage object path.
    """

    supabase = get_supabase_client()

    print(f"Uploading file to Supabase Storage: {bucket}/{path}")

    options = {
        "content-type": content_type,
        "cache-control": "3600",
        "upsert": str(upsert).lower(),
    }

    supabase.storage.from_(bucket).upload(
        path=path,
        file=file_data,
        file_options=options,
    )

    return path


# ============================================================
# DELETE
# ============================================================

def delete_file(
    bucket: str,
    path: str,
) -> None:
    """Delete a file from Supabase Storage."""

    if not path:
        return

    supabase = get_supabase_client()

    supabase.storage.from_(bucket).remove(
        [path]
    )


# ============================================================
# SIGNED URL
# ============================================================

def create_signed_url(
    bucket: str,
    path: str,
    expires_in: int = 3600,
) -> str:
    """Create a temporary signed URL for a private Storage file."""

    if not path:
        raise ValueError(
            "Storage path is required."
        )

    supabase = get_supabase_client()

    response = (
        supabase.storage
        .from_(bucket)
        .create_signed_url(
            path,
            expires_in,
        )
    )

    print(
        "Supabase signed URL response:",
        response
    )

    # Current supabase-py returns a dictionary.
    if isinstance(response, dict):

        signed_url = (
            response.get("signedUrl")
            or response.get("signedURL")
            or response.get("signed_url")
            or response.get("url")
        )

        if signed_url:

            # Some Storage API responses may return
            # a relative URL instead of a complete URL.
            if signed_url.startswith("/"):
                supabase_url = _get_config_value(
                    "SUPABASE_URL"
                )

                return (
                    supabase_url.rstrip("/")
                    + "/storage/v1"
                    + signed_url
                )

            return signed_url

    # Compatibility with response objects
    # that expose a .data property.
    data = getattr(
        response,
        "data",
        None
    )

    if isinstance(data, dict):

        signed_url = (
            data.get("signedUrl")
            or data.get("signedURL")
            or data.get("signed_url")
            or data.get("url")
        )

        if signed_url:

            if signed_url.startswith("/"):
                supabase_url = _get_config_value(
                    "SUPABASE_URL"
                )

                return (
                    supabase_url.rstrip("/")
                    + "/storage/v1"
                    + signed_url
                )

            return signed_url

    raise RuntimeError(
        "Unable to create Supabase Storage signed URL. "
        f"Response: {response!r}"
    )


# ============================================================
# COMPANY LOGO
# ============================================================

def upload_company_logo(
    file_data: bytes,
    original_filename: str,
    content_type: str,
) -> str:
    """Upload company logo and return its Storage path."""

    extension = PurePosixPath(
        original_filename
    ).suffix.lower()

    if extension not in {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
    }:
        raise ValueError(
            "Unsupported company logo format."
        )

    filename = (
        f"company_logo_"
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )

    path = f"logo/{filename}"

    return upload_file(
        COMPANY_ASSETS_BUCKET,
        path,
        file_data,
        content_type,
        upsert=False,
    )


def get_company_logo_url(
    storage_path: str,
    expires_in: int = 3600,
) -> str:
    """Return a temporary URL for a company logo."""

    return create_signed_url(
        COMPANY_ASSETS_BUCKET,
        storage_path,
        expires_in,
    )