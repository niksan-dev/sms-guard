"""
Template-based Site Invoice generation.

The Excel workbook is the source of truth for the visual layout.
Python only fills mapped cells and converts the finished workbook to PDF.
"""

from __future__ import annotations

import io
import os
import shutil
import subprocess
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any

from openpyxl import load_workbook
from sqlalchemy.orm import joinedload

from database.connection import SessionLocal
from database.site_bill import SiteBill


# Project root: <project>/services/site_invoice_template_service.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = PROJECT_ROOT / "templates" / "site_invoice"
DEFAULT_TEMPLATE = TEMPLATE_DIR / "template_1.xlsx"


# ============================================================
# TEMPLATE DISCOVERY
# ============================================================

def list_site_invoice_templates() -> dict[str, Path]:
    """Return available site invoice templates."""

    if not TEMPLATE_DIR.exists():
        return {}

    templates: dict[str, Path] = {}

    for path in sorted(TEMPLATE_DIR.glob("*.xlsx")):
        templates[path.stem] = path

    return templates


def get_default_site_invoice_template() -> Path:
    """Return the default Aadhar invoice template."""

    if not DEFAULT_TEMPLATE.exists():
        raise FileNotFoundError(
            f"Site invoice template not found: {DEFAULT_TEMPLATE}"
        )

    return DEFAULT_TEMPLATE


# ============================================================
# HELPERS
# ============================================================

def _safe(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _number(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _date_text(value: Any) -> str:
    if isinstance(value, datetime):
        value = value.date()

    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")

    return _safe(value)


def _month_text(year: int, month: int) -> str:
    return date(int(year), int(month), 1).strftime("%b %y").upper()


def _amount_words(number: float) -> str:
    """Indian-friendly English amount in words, with paise."""

    number = round(float(number or 0), 2)
    rupees = int(number)
    paise = int(round((number - rupees) * 100))

    ones = [
        "Zero", "One", "Two", "Three", "Four", "Five", "Six",
        "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve",
        "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen",
        "Eighteen", "Nineteen",
    ]
    tens = [
        "", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty",
        "Seventy", "Eighty", "Ninety",
    ]

    def under_100(n: int) -> str:
        if n < 20:
            return ones[n]
        return tens[n // 10] + (f" {ones[n % 10]}" if n % 10 else "")

    def under_1000(n: int) -> str:
        if n < 100:
            return under_100(n)
        rest = n % 100
        result = f"{ones[n // 100]} Hundred"
        if rest:
            result += f" {under_100(rest)}"
        return result

    def indian_integer(n: int) -> str:
        if n == 0:
            return "Zero"

        parts: list[str] = []

        crore = n // 10_000_000
        n %= 10_000_000
        lakh = n // 100_000
        n %= 100_000
        thousand = n // 1_000
        n %= 1_000

        if crore:
            parts.append(f"{under_1000(crore)} Crore")
        if lakh:
            parts.append(f"{under_100(lakh)} Lakh")
        if thousand:
            parts.append(f"{under_100(thousand)} Thousand")
        if n:
            parts.append(under_1000(n))

        return " ".join(parts)

    result = indian_integer(rupees) + " Rupees"

    if paise:
        result += f" and {under_100(paise)} Paise"

    return result + " Only."


def _get_attr(obj: Any, name: str, default: Any = None) -> Any:
    """Read an already-loaded Python/SQLAlchemy attribute safely."""
    if obj is None:
        return default
    return getattr(obj, name, default)


def _client_name(client: Any) -> str:
    if client is None:
        return ""

    return (
        _get_attr(client, "username")
        or _get_attr(client, "name")
        or _get_attr(client, "company_name")
        or ""
    )


def _client_pan(client: Any) -> str:
    """Return client PAN if the User model eventually provides one."""
    if client is None:
        return ""

    return (
        _get_attr(client, "pan_number")
        or _get_attr(client, "pan")
        or ""
    )


def _site_address(site: Any) -> str:
    parts = [
        _get_attr(site, "address", ""),
        _get_attr(site, "city", ""),
        _get_attr(site, "state", ""),
        _get_attr(site, "pincode", ""),
    ]

    return ", ".join(
        str(part).strip()
        for part in parts
        if part and str(part).strip()
    )


def _company_values() -> Any:
    """Load company settings without making the template service mandatory for startup."""

    try:
        from services.company_settings_service import get_company_settings
        return get_company_settings()
    except Exception:
        return None


# ============================================================
# DATABASE SNAPSHOT
# ============================================================

def _load_bill_snapshot(bill: Any) -> dict[str, Any]:
    """
    Reload the SiteBill and its Site/Client relationships while the
    SQLAlchemy session is open, then convert everything needed by the
    template into ordinary Python values.

    This deliberately prevents DetachedInstanceError when the caller
    passes a SiteBill whose original session has already been closed.
    """

    bill_id = _get_attr(bill, "id")
    if bill_id is None:
        raise ValueError("Site bill ID is required.")

    db = SessionLocal()

    try:
        loaded_bill = (
            db.query(SiteBill)
            .options(
                joinedload(SiteBill.site).joinedload(
                    __import__("database.models", fromlist=["Site"]).Site.client
                )
            )
            .filter(SiteBill.id == int(bill_id))
            .first()
        )

        if loaded_bill is None:
            raise ValueError(f"Site bill not found: {bill_id}")

        site = loaded_bill.site
        client = site.client if site is not None else None

        # Read all relationship/scalar values before closing the session.
        return {
            "bill_number": loaded_bill.bill_number,
            "billing_month": loaded_bill.billing_month,
            "billing_year": loaded_bill.billing_year,
            "bill_date": loaded_bill.bill_date,
            "total_days": loaded_bill.total_days,
            "shift_1_count": loaded_bill.shift_1_count,
            "shift_2_count": loaded_bill.shift_2_count,
            "total_shifts": loaded_bill.total_shifts,
            "monthly_rate": loaded_bill.monthly_rate,
            "shift_rate": loaded_bill.shift_rate,
            "gross_amount": loaded_bill.gross_amount,
            "cgst_amount": loaded_bill.cgst_amount,
            "sgst_amount": loaded_bill.sgst_amount,
            "total_amount": loaded_bill.total_amount,
            "site_code": _get_attr(site, "site_code", "") if site else "",
            "site_name": _get_attr(site, "name", "") if site else "",
            "site_email": _get_attr(site, "email", "") if site else "",
            "site_address": _site_address(site) if site else "",
            "customer_name": _client_name(client),
            "customer_email": _get_attr(client, "email", "") if client else "",
            "customer_pan": _client_pan(client),
        }
    finally:
        db.close()


# ============================================================
# BUILD EXCEL FROM TEMPLATE
# ============================================================

def build_site_invoice_workbook(
    bill: Any,
    template_path: str | os.PathLike | None = None,
) -> bytes:
    """
    Fill the supplied Excel invoice template and return XLSX bytes.

    Mapping follows the user's workbook:
        H5       Invoice number
        H7       Invoice date
        D5       Customer name
        D9       Customer PAN
        A10      Site address
        B13      Month text
        C15:F15  Shift 1
        C16:F16  Shift 2
        F20      Gross
        F21      CGST
        F22      SGST
        A23      Amount in words
    """

    path = Path(template_path) if template_path else get_default_site_invoice_template()

    if not path.exists():
        raise FileNotFoundError(f"Invoice template not found: {path}")

    # Keep formulas disabled for this operation; Python writes the final values.
    workbook = load_workbook(path)
    if "Invoice" not in workbook.sheetnames:
        raise ValueError(
            "The selected invoice template must contain an 'Invoice' sheet."
        )

    ws = workbook["Invoice"]

    # The mapping sheet is documentation for the developer/template editor;
    # it must never appear in the customer-facing PDF.
    if "Python Mapping" in workbook.sheetnames:
        workbook["Python Mapping"].sheet_state = "hidden"

    snapshot = _load_bill_snapshot(bill)
    settings = _company_values()

    billing_year = int(snapshot["billing_year"] or date.today().year)
    billing_month = int(snapshot["billing_month"] or date.today().month)

    invoice_date = snapshot["bill_date"] or date.today()
    invoice_number = snapshot["bill_number"]

    # --------------------------------------------------------
    # COMPANY SETTINGS
    # --------------------------------------------------------
    company_name = (
        _get_attr(settings, "company_name", "")
        or "AADHAR SECURITY SERVICES"
    )

    company_address = _get_attr(settings, "address", "")
    company_city = _get_attr(settings, "city", "")
    company_state = _get_attr(settings, "state", "")
    company_pincode = _get_attr(settings, "pincode", "")
    company_phone = _get_attr(settings, "phone", "")
    company_pan = (
        _get_attr(settings, "pan_number", "")
        or _get_attr(settings, "pan", "")
    )
    owner_name = _get_attr(settings, "owner_name", "")
    account_number = _get_attr(settings, "account_number", "")
    ifsc_code = _get_attr(settings, "ifsc_code", "")
    branch_name = _get_attr(settings, "branch_name", "")

    full_company_address = ", ".join(
        str(part).strip()
        for part in [
            company_address,
            company_city,
            company_state,
            company_pincode,
        ]
        if part and str(part).strip()
    )

    # --------------------------------------------------------
    # HEADER / CLIENT
    # --------------------------------------------------------
    ws["C2"] = company_name

    if full_company_address:
        ws["C3"] = full_company_address

    if company_phone:
        ws["C4"] = company_phone

    ws["A5"] = f"Bill From,\n{company_name}"

    customer_name = snapshot["customer_name"]
    ws["D5"] = f"Bill To,\n{customer_name}" if customer_name else "Bill To,\n"

    ws["H5"] = invoice_number
    ws["H7"] = _date_text(invoice_date)

    # The current project has no PAN column on User. Leave this blank unless
    # a PAN attribute is added later. Never substitute the company's PAN.
    customer_pan = snapshot["customer_pan"]
    ws["D9"] = f"PAN:- {customer_pan}" if customer_pan else "PAN:- "

    site_address = snapshot["site_address"]
    site_label = "Site Address:-"
    ws["A10"] = (
        f"{site_label} {site_address}"
        if site_address
        else site_label
    )

    # --------------------------------------------------------
    # BILLING DATA
    # --------------------------------------------------------
    days = int(snapshot["total_days"] or 0)
    shift_rate = _number(snapshot["shift_rate"])
    shift_1_count = int(snapshot["shift_1_count"] or 0)
    shift_2_count = int(snapshot["shift_2_count"] or 0)

    shift_1_amount = round(shift_rate * shift_1_count, 2)
    shift_2_amount = round(shift_rate * shift_2_count, 2)

    # Main month row.
    ws["B13"] = (
        f"For the month of\n{_month_text(billing_year, billing_month)}"
    )

    # Shift 1 row.
    ws["B15"] = "Day/Night"
    ws["C15"] = "01"
    ws["D15"] = shift_1_count
    ws["E15"] = days
    ws["F15"] = shift_1_amount

    # Shift 2 row.
    ws["B16"] = "Day/Night"
    ws["C16"] = "01"
    ws["D16"] = shift_2_count
    ws["E16"] = days
    ws["F16"] = shift_2_amount

    gross_amount = _number(snapshot["gross_amount"])
    cgst_amount = _number(snapshot["cgst_amount"])
    sgst_amount = _number(snapshot["sgst_amount"])
    total_amount = _number(snapshot["total_amount"])

    # --------------------------------------------------------
    # TOTALS
    # --------------------------------------------------------
    ws["F20"] = gross_amount
    ws["F21"] = cgst_amount if cgst_amount else "-"
    ws["F22"] = sgst_amount if sgst_amount else "-"
    ws["A23"] = (
        f"Total Amt In Word :- {_amount_words(total_amount)}"
    )

    # --------------------------------------------------------
    # BANK / SIGNATURE
    # --------------------------------------------------------
    bank_lines = [
        "BANK DETAILS:-",
        "",
        company_name,
    ]

    if account_number:
        bank_lines.append(f"ACC NO :- {account_number}")
    if ifsc_code:
        bank_lines.append(f"IFSC CODE:- {ifsc_code}")
    if branch_name:
        bank_lines.append(f"BRANCH:- {branch_name}.")

    ws["A24"] = "\n".join(bank_lines)

    signature_name = owner_name or "Proprietor"
    ws["E24"] = (
        f"FOR {company_name}.\n\n\n{signature_name}"
    )

    # --------------------------------------------------------
    # PAGE / PRINT SETTINGS
    # --------------------------------------------------------
    # The workbook is the visual template. Keep its design, but force the
    # invoice to print as a single A4 page.
    ws.print_area = "A1:H38"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_margins.left = 0.20
    ws.page_margins.right = 0.20
    ws.page_margins.top = 0.20
    ws.page_margins.bottom = 0.20

    # --------------------------------------------------------
    # FORMATTING
    # --------------------------------------------------------
    # Preserve the template's formatting. Only set number formats for values
    # that Python writes so LibreOffice displays them consistently.
    for cell in ("F15", "F16", "F20", "F21", "F22"):
        ws[cell].number_format = '#,##0.00'

    # Force recalculation if the workbook contains any remaining formulas.
    workbook.calculation.fullCalcOnLoad = True
    workbook.calculation.forceFullCalc = True
    workbook.calculation.calcMode = "auto"

    output = io.BytesIO()
    workbook.save(output)
    return output.getvalue()


# ============================================================
# CONVERT XLSX -> PDF
# ============================================================

def _find_soffice() -> str | None:
    candidates = [
        shutil.which("soffice"),
        shutil.which("libreoffice"),
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate

    return None


def _excel_com_to_pdf(xlsx_data: bytes) -> bytes | None:
    """Use installed Microsoft Excel on Windows when available."""

    if os.name != "nt":
        return None

    try:
        import win32com.client  # type: ignore
    except ImportError:
        return None

    excel = None
    workbook = None

    with tempfile.TemporaryDirectory(prefix="site_invoice_excel_") as temp_dir:
        temp_path = Path(temp_dir)
        xlsx_path = temp_path / "site_invoice.xlsx"
        pdf_path = temp_path / "site_invoice.pdf"
        xlsx_path.write_bytes(xlsx_data)

        try:
            excel = win32com.client.DispatchEx("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False

            workbook = excel.Workbooks.Open(
                str(xlsx_path),
                ReadOnly=True
            )

            # 0 = xlTypePDF
            workbook.ExportAsFixedFormat(
                0,
                str(pdf_path),
                0,
                True,
                False,
            )

            if pdf_path.exists():
                return pdf_path.read_bytes()

        except Exception:
            return None

        finally:
            if workbook is not None:
                try:
                    workbook.Close(False)
                except Exception:
                    pass

            if excel is not None:
                try:
                    excel.Quit()
                except Exception:
                    pass

    return None


def xlsx_bytes_to_pdf(xlsx_data: bytes) -> bytes:
    """Convert an XLSX byte stream to PDF.

    Windows: prefer Microsoft Excel if pywin32 + Excel are available.
    Otherwise fall back to LibreOffice.
    """

    excel_pdf = _excel_com_to_pdf(xlsx_data)
    if excel_pdf:
        return excel_pdf

    soffice = _find_soffice()

    if not soffice:
        raise RuntimeError(
            "Neither Microsoft Excel nor LibreOffice is available for "
            "Excel-to-PDF conversion. Install LibreOffice, or install "
            "pywin32 with Microsoft Excel on Windows."
        )

    with tempfile.TemporaryDirectory(prefix="site_invoice_") as temp_dir:
        temp_path = Path(temp_dir)
        xlsx_path = temp_path / "site_invoice.xlsx"

        xlsx_path.write_bytes(xlsx_data)

        profile_dir = temp_path / "lo_profile"
        profile_dir.mkdir()

        command = [
            soffice,
            "--headless",
            f"-env:UserInstallation=file:///{profile_dir.as_posix()}",
            "--convert-to",
            "pdf",
            "--outdir",
            str(temp_path),
            str(xlsx_path),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60,
        )

        pdf_path = temp_path / "site_invoice.pdf"

        if result.returncode != 0 or not pdf_path.exists():
            raise RuntimeError(
                "Excel template PDF conversion failed. "
                f"stdout={result.stdout.strip()} "
                f"stderr={result.stderr.strip()}"
            )

        return pdf_path.read_bytes()


# ============================================================
# PUBLIC PDF API
# ============================================================

def generate_site_bill_pdf_from_template(
    bill: Any,
    template_path: str | os.PathLike | None = None,
) -> bytes:
    """Generate the final site bill PDF from the selected Excel template."""

    xlsx_data = build_site_invoice_workbook(
        bill=bill,
        template_path=template_path,
    )

    return xlsx_bytes_to_pdf(xlsx_data)
