from pathlib import Path
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile
from datetime import date

from sqlalchemy import or_

from database.connection import SessionLocal
from database.models import Guard
from database.guard_document import GuardDocument


PROJECT_ROOT = Path(__file__).resolve().parent.parent
GUARD_DOCUMENT_DIR = PROJECT_ROOT / "uploads" / "guard_documents"
GUARD_DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)


DOCUMENT_TYPES = [
    "Aadhaar Card",
    "PAN Card",
    "Voter ID",
    "Driving License",
    "Police Verification",
    "Address Proof",
    "Medical Certificate",
    "Training Certificate",
    "Bank Document",
    "Passport",
    "Other",
]

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _clean(value):
    return str(value).strip() if value is not None else ""


def mask_document_number(value, document_type=""):
    value = _clean(value)
    if not value:
        return ""

    compact = value.replace(" ", "")
    document_type = _clean(document_type).lower()

    if "aadhaar" in document_type and len(compact) == 12:
        return f"XXXX XXXX {compact[-4:]}"

    if "pan" in document_type and len(compact) >= 5:
        return f"{'X' * max(0, len(compact) - 5)}{compact[-5:]}"

    if len(compact) <= 4:
        return "X" * len(compact)

    return f"{'X' * (len(compact) - 4)}{compact[-4:]}"


def validate_document_number(document_type, document_number):
    document_type = _clean(document_type)
    value = _clean(document_number).replace(" ", "").upper()

    if not value:
        return True, ""

    if document_type == "Aadhaar Card":
        if not value.isdigit() or len(value) != 12:
            return False, "Aadhaar number must contain exactly 12 digits."

    elif document_type == "PAN Card":
        if len(value) != 10 or not (
            value[:5].isalpha()
            and value[5:9].isdigit()
            and value[9].isalpha()
        ):
            return False, "PAN must be in the format ABCDE1234F."

    elif document_type == "Voter ID":
        if len(value) < 6 or len(value) > 20:
            return False, "Voter ID must contain 6 to 20 characters."

    return True, ""


def get_guard_documents(guard_id):
    db = SessionLocal()
    try:
        return (
            db.query(GuardDocument)
            .filter(
                GuardDocument.guard_id == guard_id,
                GuardDocument.status == "Active",
            )
            .order_by(GuardDocument.document_type.asc())
            .all()
        )
    finally:
        db.close()


def get_guard_document(guard_id, document_type):
    db = SessionLocal()
    try:
        return (
            db.query(GuardDocument)
            .filter(
                GuardDocument.guard_id == guard_id,
                GuardDocument.document_type == document_type,
                GuardDocument.status == "Active",
            )
            .first()
        )
    finally:
        db.close()


def _save_document_file(uploaded_file, employee_id, document_type):
    if not uploaded_file:
        return None

    original_name = Path(uploaded_file.name or "document").name
    extension = Path(original_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Only PDF, JPG, JPEG, PNG and WEBP documents are allowed."
        )

    size = int(getattr(uploaded_file, "size", 0) or 0)
    if size <= 0:
        data = uploaded_file.getbuffer()
        size = len(data)
    else:
        data = uploaded_file.getbuffer()

    if size > MAX_FILE_SIZE:
        raise ValueError("Each document must be 10 MB or smaller.")

    safe_type = "".join(
        c if c.isalnum() else "_"
        for c in document_type.lower()
    ).strip("_")

    guard_dir = GUARD_DOCUMENT_DIR / str(employee_id)
    guard_dir.mkdir(parents=True, exist_ok=True)

    filename = (
        f"{safe_type}_"
        f"{uuid4().hex[:12]}"
        f"{extension}"
    )

    file_path = guard_dir / filename
    file_path.write_bytes(data)

    return (
        file_path.relative_to(PROJECT_ROOT).as_posix(),
        original_name,
        getattr(uploaded_file, "type", None),
        size,
    )


def _delete_file(relative_path):
    if not relative_path:
        return

    try:
        path = PROJECT_ROOT / relative_path
        if path.exists() and path.is_file():
            path.unlink()
    except Exception:
        pass


def save_guard_document(
    guard_id,
    document_type,
    document_number=None,
    uploaded_file=None,
    expiry_date=None,
):
    document_type = _clean(document_type)
    document_number = _clean(document_number).replace(" ", "").upper()

    if document_type not in DOCUMENT_TYPES:
        return False, "Invalid document type."

    valid, message = validate_document_number(
        document_type,
        document_number,
    )
    if not valid:
        return False, message

    if not uploaded_file:
        return False, "Please select a document file."

    db = SessionLocal()
    new_relative_path = None
    old_relative_path = None

    try:
        guard = (
            db.query(Guard)
            .filter(Guard.id == guard_id)
            .first()
        )

        if not guard:
            return False, "Guard not found."

        saved = _save_document_file(
            uploaded_file,
            guard.employee_id,
            document_type,
        )
        (
            new_relative_path,
            original_filename,
            mime_type,
            file_size,
        ) = saved

        existing = (
            db.query(GuardDocument)
            .filter(
                GuardDocument.guard_id == guard_id,
                GuardDocument.document_type == document_type,
            )
            .first()
        )

        if existing:
            old_relative_path = existing.file_path
            existing.document_number = document_number or None
            existing.file_path = new_relative_path
            existing.original_filename = original_filename
            existing.mime_type = mime_type
            existing.file_size = file_size
            existing.expiry_date = expiry_date
            existing.status = "Active"
            message = f"{document_type} replaced successfully."
        else:
            db.add(
                GuardDocument(
                    guard_id=guard_id,
                    document_type=document_type,
                    document_number=document_number or None,
                    file_path=new_relative_path,
                    original_filename=original_filename,
                    mime_type=mime_type,
                    file_size=file_size,
                    expiry_date=expiry_date,
                    status="Active",
                )
            )
            message = f"{document_type} uploaded successfully."

        db.commit()

        if old_relative_path and old_relative_path != new_relative_path:
            _delete_file(old_relative_path)

        return True, message

    except Exception as exc:
        db.rollback()
        if new_relative_path:
            _delete_file(new_relative_path)
        return False, str(exc)
    finally:
        db.close()


def delete_guard_document(document_id):
    db = SessionLocal()
    try:
        document = (
            db.query(GuardDocument)
            .filter(GuardDocument.id == document_id)
            .first()
        )

        if not document:
            return False, "Document not found."

        relative_path = document.file_path
        db.delete(document)
        db.commit()
        _delete_file(relative_path)
        return True, "Document deleted successfully."

    except Exception as exc:
        db.rollback()
        return False, str(exc)
    finally:
        db.close()


def get_guard_document_file(document_id):
    db = SessionLocal()
    try:
        document = (
            db.query(GuardDocument)
            .filter(
                GuardDocument.id == document_id,
                GuardDocument.status == "Active",
            )
            .first()
        )
        if not document:
            return None, None

        path = PROJECT_ROOT / document.file_path
        if not path.exists():
            return None, document

        return path, document
    finally:
        db.close()


def get_document_readiness(guard_id):
    documents = get_guard_documents(guard_id)
    uploaded_types = {doc.document_type for doc in documents}
    required_types = [
        "Aadhaar Card",
        "PAN Card",
        "Voter ID",
        "Police Verification",
        "Address Proof",
        "Medical Certificate",
        "Training Certificate",
    ]
    completed = sum(
        1 for item in required_types if item in uploaded_types
    )
    return completed, len(required_types), uploaded_types


def create_guard_documents_zip(guard_id):
    """Create a temporary ZIP containing all active guard documents."""
    db = SessionLocal()
    try:
        guard = (
            db.query(Guard)
            .filter(Guard.id == guard_id)
            .first()
        )
        if not guard:
            raise ValueError("Guard not found.")

        documents = (
            db.query(GuardDocument)
            .filter(
                GuardDocument.guard_id == guard_id,
                GuardDocument.status == "Active",
            )
            .order_by(GuardDocument.document_type.asc())
            .all()
        )

        if not documents:
            raise ValueError("No guard documents have been uploaded.")

        export_dir = PROJECT_ROOT / "uploads" / "guard_document_exports"
        export_dir.mkdir(parents=True, exist_ok=True)

        zip_path = export_dir / (
            f"{guard.employee_id}_documents_"
            f"{uuid4().hex[:10]}.zip"
        )

        with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
            for document in documents:
                source = PROJECT_ROOT / document.file_path
                if not source.exists():
                    continue
                archive.write(
                    source,
                    arcname=(
                        f"{document.document_type}/"
                        f"{document.original_filename}"
                    ),
                )

        if zip_path.stat().st_size == 0:
            raise ValueError("Uploaded document files could not be found.")

        return zip_path

    finally:
        db.close()
