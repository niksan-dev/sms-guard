"""Fast ReportLab site invoice renderer.

The Excel invoice template is kept as a visual/reference template only.
No Microsoft Excel, COM, or LibreOffice conversion is performed at runtime.

The public API intentionally keeps the same names used by the Billing & Payroll
page so the page does not need to know how the PDF is rendered.
"""

from __future__ import annotations

import io
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from sqlalchemy.orm import joinedload

from database.connection import SessionLocal
from database.company_settings import CompanySettings
from database.models import Site
from database.site_bill import SiteBill


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = PROJECT_ROOT / "templates" / "site_invoice"
DEFAULT_TEMPLATE = TEMPLATE_DIR / "template_1.xlsx"
EXPORT_DIR = PROJECT_ROOT / "uploads" / "site_invoice_exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# ReportLab fonts
# ---------------------------------------------------------------------------

_FONT_REGULAR = "Helvetica"
_FONT_BOLD = "Helvetica-Bold"


def _register_fonts() -> None:
    """Register a Unicode font if one is available; otherwise use Helvetica."""
    global _FONT_REGULAR, _FONT_BOLD

    candidates = [
        (
            PROJECT_ROOT / "assets" / "fonts" / "DejaVuSans.ttf",
            PROJECT_ROOT / "assets" / "fonts" / "DejaVuSans-Bold.ttf",
        ),
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ),
        (
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("C:/Windows/Fonts/arialbd.ttf"),
        ),
    ]

    for regular, bold in candidates:
        if regular.is_file() and bold.is_file():
            try:
                pdfmetrics.registerFont(TTFont("InvoiceUnicode", str(regular)))
                pdfmetrics.registerFont(TTFont("InvoiceUnicodeBold", str(bold)))
                _FONT_REGULAR = "InvoiceUnicode"
                _FONT_BOLD = "InvoiceUnicodeBold"
                return
            except Exception:
                continue


_register_fonts()


# ---------------------------------------------------------------------------
# Template discovery - retained for compatibility with Billing & Payroll
# ---------------------------------------------------------------------------


def list_site_invoice_templates() -> dict[str, Path]:
    if not TEMPLATE_DIR.exists():
        return {}
    return {
        path.stem: path
        for path in sorted(TEMPLATE_DIR.glob("*.xlsx"))
    }


def get_default_site_invoice_template() -> Path:
    if not DEFAULT_TEMPLATE.exists():
        # Fall back to the first reference template if the historical default
        # name is different.
        templates = list_site_invoice_templates()
        if templates:
            return next(iter(templates.values()))
        raise FileNotFoundError(
            f"Site invoice reference template not found: {DEFAULT_TEMPLATE}"
        )
    return DEFAULT_TEMPLATE


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


def _site_address(site: Any) -> str:
    parts = [
        getattr(site, "address", ""),
        getattr(site, "city", ""),
        getattr(site, "state", ""),
        getattr(site, "pincode", ""),
    ]
    return ", ".join(
        str(part).strip()
        for part in parts
        if part and str(part).strip()
    )


def _client_name(client: Any) -> str:
    if client is None:
        return ""
    return (
        getattr(client, "username", None)
        or getattr(client, "name", None)
        or getattr(client, "company_name", None)
        or ""
    )


def _client_pan(client: Any) -> str:
    if client is None:
        return ""
    return (
        getattr(client, "pan_number", None)
        or getattr(client, "pan", None)
        or ""
    )


def _company_values() -> dict[str, Any]:
    db = SessionLocal()
    try:
        settings = (
            db.query(CompanySettings)
            .order_by(CompanySettings.id.asc())
            .first()
        )
        if settings is None:
            raise CompanySettingsRequiredError(
                "Company settings are not configured. "
                "Please configure Company Settings before generating an invoice."
            )
        return {
            "id": settings.id,
            "company_name": settings.company_name,
            "owner_name": settings.owner_name,
            "phone": settings.phone,
            "email": settings.email,
            "address": settings.address,
            "city": settings.city,
            "state": settings.state,
            "pincode": settings.pincode,
            "gst_number": settings.gst_number,
            "cgst_rate": getattr(settings, "cgst_rate", 9.0),
            "sgst_rate": getattr(settings, "sgst_rate", 9.0),
            "pan_number": settings.pan_number,
            "bank_name": settings.bank_name,
            "account_holder_name": settings.account_holder_name,
            "account_number": settings.account_number,
            "ifsc_code": settings.ifsc_code,
            "branch_name": settings.branch_name,
            "invoice_prefix": settings.invoice_prefix,
            "gst_invoice_prefix": settings.gst_invoice_prefix,
            "logo_path": settings.logo_path,
            "updated_at": settings.updated_at,
        }
    finally:
        db.close()


class CompanySettingsRequiredError(RuntimeError):
    pass


def _resolve_logo_path(value: Any) -> Path | None:
    if not value:
        return None
    path = Path(str(value))
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    try:
        path = path.resolve()
    except OSError:
        return None
    return path if path.is_file() else None


def _load_bill_snapshot(bill: Any) -> dict[str, Any]:
    bill_id = getattr(bill, "id", None)
    if bill_id is None:
        raise ValueError("Site bill ID is required.")

    db = SessionLocal()
    try:
        loaded_bill = (
            db.query(SiteBill)
            .options(
                joinedload(SiteBill.site).joinedload(Site.client)
            )
            .filter(SiteBill.id == int(bill_id))
            .first()
        )
        if loaded_bill is None:
            raise ValueError(f"Site bill not found: {bill_id}")

        site = loaded_bill.site
        client = site.client if site is not None else None
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
            "site_code": getattr(site, "site_code", "") if site else "",
            "site_name": getattr(site, "name", "") if site else "",
            "site_email": getattr(site, "email", "") if site else "",
            "site_address": _site_address(site) if site else "",
            "customer_name": _client_name(client),
            "customer_email": getattr(client, "email", "") if client else "",
            "customer_pan": _client_pan(client),
            "updated_at": loaded_bill.updated_at,
        }
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Text layout helpers
# ---------------------------------------------------------------------------


def _wrap_text(text: Any, font: str, size: float, max_width: float) -> list[str]:
    value = _safe(text).replace("\r", "")
    if not value:
        return [""]

    lines: list[str] = []
    for paragraph in value.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue

        current = ""
        for word in words:
            candidate = word if not current else f"{current} {word}"
            if pdfmetrics.stringWidth(candidate, font, size) <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                # Break a very long token if necessary.
                current = ""
                chunk = ""
                for char in word:
                    test = chunk + char
                    if pdfmetrics.stringWidth(test, font, size) <= max_width:
                        chunk = test
                    else:
                        if chunk:
                            lines.append(chunk)
                        chunk = char
                current = chunk
        if current:
            lines.append(current)
    return lines or [""]


def _draw_wrapped(
    c: canvas.Canvas,
    text: Any,
    x: float,
    y: float,
    width: float,
    font: str = _FONT_REGULAR,
    size: float = 10,
    leading: float | None = None,
    align: str = "left",
    max_lines: int | None = None,
) -> float:
    leading = leading or size * 1.2
    lines = _wrap_text(text, font, size, width)
    if max_lines is not None:
        lines = lines[:max_lines]

    c.setFont(font, size)
    for line in lines:
        if align == "center":
            c.drawCentredString(x + width / 2, y, line)
        elif align == "right":
            c.drawRightString(x + width, y, line)
        else:
            c.drawString(x, y, line)
        y -= leading
    return y


def _draw_centered_cell_text(
    c: canvas.Canvas,
    text: Any,
    x: float,
    y: float,
    width: float,
    height: float,
    font: str,
    size: float,
    leading: float | None = None,
) -> None:
    leading = leading or size * 1.15
    lines = _wrap_text(text, font, size, width - 8)
    total = len(lines) * leading
    baseline = y + (height + total) / 2 - leading
    c.setFont(font, size)
    for line in lines:
        c.drawCentredString(x + width / 2, baseline, line)
        baseline -= leading


def _draw_left_cell_text(
    c: canvas.Canvas,
    text: Any,
    x: float,
    y: float,
    width: float,
    height: float,
    font: str,
    size: float,
    padding: float = 5,
) -> None:
    leading = size * 1.15
    lines = _wrap_text(text, font, size, max(1, width - 2 * padding))
    total = len(lines) * leading
    baseline = y + (height + total) / 2 - leading
    c.setFont(font, size)
    for line in lines:
        c.drawString(x + padding, baseline, line)
        baseline -= leading


# ---------------------------------------------------------------------------
# Invoice renderer
# ---------------------------------------------------------------------------


def _draw_invoice(snapshot: dict[str, Any], settings: dict[str, Any]) -> bytes:
    """Render the reference Excel invoice geometry directly with ReportLab."""

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    page_w, page_h = A4

    # Excel print area A1:H38 is reproduced inside a compact 7.5 mm margin.
    left = 21.5
    right = 21.5
    top = 18.0
    bottom = 18.0
    x0 = left
    y_top = page_h - top
    usable_w = page_w - left - right

    # Column proportions based on the Excel template's A:H widths:
    # 7, 27, 10, 14, 18, 18, 14, 14.
    excel_widths = [7, 27, 10, 14, 18, 18, 14, 14]
    scale = usable_w / sum(excel_widths)
    col = [w * scale for w in excel_widths]
    xs = [x0]
    for width in col:
        xs.append(xs[-1] + width)

    # Row heights based on the Excel template. Rows 1-10 are slightly taller;
    # rows 11-38 follow the 25-point template rhythm.
    excel_heights = [
        24, 48, 28, 28,
        20, 20, 20, 20, 20, 32,
        *([25] * 28),
    ]
    row_scale = (page_h - top - bottom) / sum(excel_heights)
    row_h = [h * row_scale for h in excel_heights]
    ys = [y_top]
    for height in row_h:
        ys.append(ys[-1] - height)

    def rect(c1: int, r1: int, c2: int, r2: int, fill=None, stroke=True, width=0.55):
        x = xs[c1]
        y = ys[r2]
        w = xs[c2 + 1] - x
        h = ys[r1] - y
        if fill is not None:
            c.setFillColor(fill)
            c.setStrokeColor(colors.black if stroke else fill)
            c.setLineWidth(width)
            c.rect(x, y, w, h, fill=1, stroke=1 if stroke else 0)
        elif stroke:
            c.setStrokeColor(colors.black)
            c.setLineWidth(width)
            c.rect(x, y, w, h, fill=0, stroke=1)
        return x, y, w, h

    def cell(c1, r1, c2=None, r2=None):
        if c2 is None:
            c2 = c1
        if r2 is None:
            r2 = r1
        return xs[c1], ys[r2 + 1], xs[c2 + 1] - xs[c1], ys[r1] - ys[r2 + 1]

    # Base borders for the complete printable area.
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.55)
    c.rect(x0, ys[-1], usable_w, y_top - ys[-1], fill=0, stroke=1)

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    x, y, w, h = cell(0, 0, 7, 0)
    c.setFont(_FONT_BOLD, 13)
    c.drawCentredString(x + w / 2, y + h / 2 - 4, "TAX INVOICE")

    # Logo A2:B4, company details C2:H4.
    logo_x, logo_y, logo_w, logo_h = cell(0, 1, 1, 3)
    logo_path = _resolve_logo_path(settings.get("logo_path"))
    if logo_path:
        try:
            image = ImageReader(str(logo_path))
            iw, ih = image.getSize()
            ratio = min((logo_w - 8) / iw, (logo_h - 8) / ih)
            dw, dh = iw * ratio, ih * ratio
            c.drawImage(
                image,
                logo_x + (logo_w - dw) / 2,
                logo_y + (logo_h - dh) / 2,
                width=dw,
                height=dh,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            pass

    company_name = _safe(settings.get("company_name"))
    company_address = ", ".join(
        str(v).strip()
        for v in [
            settings.get("address"),
            settings.get("city"),
            settings.get("state"),
            settings.get("pincode"),
        ]
        if v and str(v).strip()
    )
    contact = " / ".join(
        str(v).strip()
        for v in [settings.get("phone"), settings.get("email")]
        if v and str(v).strip()
    )

    cx, cy, cw, ch = cell(2, 1, 7, 1)
    _draw_centered_cell_text(c, company_name, cx, cy, cw, ch, _FONT_BOLD, 17)
    cx, cy, cw, ch = cell(2, 2, 7, 2)
    _draw_centered_cell_text(c, company_address, cx, cy, cw, ch, _FONT_BOLD, 9.5)
    cx, cy, cw, ch = cell(2, 3, 7, 3)
    _draw_centered_cell_text(c, contact, cx, cy, cw, ch, _FONT_BOLD, 10.5)

    # Bill From / Bill To / Invoice metadata.
    rect(0, 4, 2, 7)
    rect(3, 4, 5, 7)
    rect(6, 4, 6, 5)
    rect(7, 4, 7, 5)
    rect(6, 6, 6, 7)
    rect(7, 6, 7, 7)

    bx, by, bw, bh = cell(0, 4, 2, 7)
    bill_from = f"Bill From,\n{company_name}"
    _draw_left_cell_text(c, bill_from, bx, by, bw, bh, _FONT_BOLD, 9.5)

    tx, ty, tw, th = cell(3, 4, 5, 7)
    bill_to = f"Bill To,\n{_safe(snapshot.get('customer_name'))}"
    site_name = _safe(snapshot.get("site_name"))
    if site_name:
        bill_to += f"\nSite: {site_name}"
    _draw_left_cell_text(c, bill_to, tx, ty, tw, th, _FONT_BOLD, 9.5)

    gx, gy, gw, gh = cell(6, 4, 6, 5)
    _draw_left_cell_text(c, "Invoice\nNo.", gx, gy, gw, gh, _FONT_BOLD, 9.5)
    hx, hy, hw, hh = cell(7, 4, 7, 5)
    _draw_left_cell_text(c, snapshot.get("bill_number"), hx, hy, hw, hh, _FONT_REGULAR, 9.5)

    gx, gy, gw, gh = cell(6, 6, 6, 7)
    _draw_left_cell_text(c, "Invoice\nDate", gx, gy, gw, gh, _FONT_BOLD, 9.5)
    hx, hy, hw, hh = cell(7, 6, 7, 7)
    _draw_left_cell_text(c, _date_text(snapshot.get("bill_date") or date.today()), hx, hy, hw, hh, _FONT_REGULAR, 9.5)

    # PAN row and project/site address.
    rect(0, 8, 2, 8)
    rect(3, 8, 5, 8)
    rect(6, 8, 7, 8)
    px, py, pw, ph = cell(0, 8, 2, 8)
    pan = _safe(settings.get("pan_number"))
    _draw_left_cell_text(c, f"PAN:- {pan}" if pan else "PAN:-", px, py, pw, ph, _FONT_REGULAR, 9.5)

    if snapshot.get("customer_pan"):
        cx, cy, cw, ch = cell(3, 8, 5, 8)
        _draw_left_cell_text(c, f"PAN:- {snapshot['customer_pan']}", cx, cy, cw, ch, _FONT_REGULAR, 9.5)

    ax, ay, aw, ah = cell(0, 9, 7, 9)
    site_address = snapshot.get("site_address") or ""
    _draw_left_cell_text(c, f"Project Add :- {site_address}", ax, ay, aw, ah, _FONT_REGULAR, 9.2)

    # ------------------------------------------------------------------
    # Particulars table rows 11-19
    # ------------------------------------------------------------------
    for r in range(10, 19):
        rect(0, r, 7, r)
    # Vertical grid lines A:H through rows 11-19.
    for ci in range(1, 8):
        c.line(xs[ci], ys[10], xs[ci], ys[19])

    headers = ["Sr.\nNo.", "PARTICULARS", "UNIT", "QUANTITY", "No. Of Days", "AMOUNT"]
    for idx, text in enumerate(headers):
        cx = xs[idx]
        cw = xs[idx + 1] - xs[idx]
        # F:H is merged for amount.
        if idx == 5:
            cx, cw = xs[5], xs[8] - xs[5]
        _draw_centered_cell_text(c, text, cx, ys[11], cw, row_h[10], _FONT_BOLD, 9.5)

    # F11:H11 merged, remove internal lines within header amount area.
    c.setFillColor(colors.white)
    c.rect(xs[5], ys[11], xs[8] - xs[5], row_h[10], fill=1, stroke=0)
    c.setStrokeColor(colors.black)
    c.rect(xs[5], ys[11], xs[8] - xs[5], row_h[10], fill=0, stroke=1)
    _draw_centered_cell_text(c, "AMOUNT", xs[5], ys[11], xs[8] - xs[5], row_h[10], _FONT_BOLD, 9.5)

    # The white fill used above for the merged AMOUNT header must not carry
    # into the remaining invoice content. Otherwise all subsequent dynamic
    # values are drawn in white and appear to be missing from the PDF.
    c.setFillColor(colors.black)

    # Row 12: section title (B12:H12 is merged in the reference workbook).
    rect(0, 11, 0, 11)
    rect(1, 11, 7, 11)
    _draw_centered_cell_text(c, "A", xs[0], ys[12], col[0], row_h[11], _FONT_BOLD, 9.5)
    _draw_left_cell_text(c, "Providing Security Guard", xs[1], ys[12], xs[8] - xs[1], row_h[11], _FONT_BOLD, 9.5)

    # Rows 13-14: A13:A14 and B13:B14 are merged in the reference workbook.
    rect(0, 12, 0, 13)
    rect(1, 12, 7, 13)
    _draw_centered_cell_text(c, "1", xs[0], ys[14], col[0], row_h[12] + row_h[13], _FONT_REGULAR, 9.5)
    month_text = f"For the month of\n{_month_text(snapshot['billing_year'], snapshot['billing_month'])}"
    _draw_left_cell_text(c, month_text, xs[1], ys[14], xs[8] - xs[1], row_h[12] + row_h[13], _FONT_REGULAR, 9.5)

    # Rows 15-19: shift lines. The original template uses Day/Night and
    # leaves unused rows blank. We render Shift 1 and Shift 2 explicitly.
    shift_rows = [
        (14, "Day/Night", snapshot.get("shift_1_count", 0)),
        (15, "Day/Night", snapshot.get("shift_2_count", 0)),
    ]
    shift_rate = _number(snapshot.get("shift_rate"))
    total_days = int(snapshot.get("total_days") or 0)

    for r in range(14, 19):
        # Clear / draw row borders.
        rect(0, r, 7, r)
        for ci in range(1, 7):
            c.line(xs[ci], ys[r], xs[ci], ys[r + 1])

    for r, unit, quantity in shift_rows:
        values = [
            "",
            unit,
            "01",
            f"{int(quantity or 0):02d}",
            str(total_days),
            f"₹ {shift_rate * int(quantity or 0):,.2f}",
        ]
        _draw_centered_cell_text(c, values[0], xs[0], ys[r + 1], col[0], row_h[r], _FONT_REGULAR, 9.5)
        _draw_centered_cell_text(c, values[1], xs[1], ys[r + 1], col[1], row_h[r], _FONT_REGULAR, 9.5)
        _draw_centered_cell_text(c, values[2], xs[2], ys[r + 1], col[2], row_h[r], _FONT_REGULAR, 9.5)
        _draw_centered_cell_text(c, values[3], xs[3], ys[r + 1], col[3], row_h[r], _FONT_REGULAR, 9.5)
        _draw_centered_cell_text(c, values[4], xs[4], ys[r + 1], col[4], row_h[r], _FONT_REGULAR, 9.5)
        _draw_left_cell_text(c, values[5], xs[5], ys[r + 1], xs[8] - xs[5], row_h[r], _FONT_REGULAR, 9.5, padding=5)

    # ------------------------------------------------------------------
    # Totals rows 20-22
    # ------------------------------------------------------------------
    for r in (19, 20, 21):
        rect(0, r, 4, r)
        rect(5, r, 7, r)
        c.setStrokeColor(colors.black)
        c.line(xs[5], ys[r], xs[5], ys[r + 1])

    gross = _number(snapshot.get("gross_amount"))
    cgst = _number(snapshot.get("cgst_amount"))
    sgst = _number(snapshot.get("sgst_amount"))

    cgst_rate = _number(settings.get("cgst_rate", 9.0))
    sgst_rate = _number(settings.get("sgst_rate", 9.0))
    labels = [
        "Gross Bill Amt.",
        f"Add : CGST @ {cgst_rate:g} % Of Gross",
        f"Add : SGST @ {sgst_rate:g} % Of Gross",
    ]
    amounts = [gross, cgst, sgst]
    for i, (label, amount) in enumerate(zip(labels, amounts), start=19):
        lx, ly, lw, lh = cell(0, i, 4, i)
        _draw_left_cell_text(c, label, lx, ly, lw, lh, _FONT_BOLD if i == 19 else _FONT_REGULAR, 9.5, padding=5)
        ax, ay, aw, ah = cell(5, i, 7, i)
        _draw_left_cell_text(c, f"₹ {amount:,.2f}" if amount else "-", ax, ay, aw, ah, _FONT_REGULAR if i != 19 else _FONT_BOLD, 9.5, padding=5)

    # ------------------------------------------------------------------
    # Amount in words
    # ------------------------------------------------------------------
    # Row 23: amount in words on the left and Grand Total on the right,
    # matching the generated invoice layout used by Billing & Payroll.
    rect(0, 22, 4, 22)
    rect(5, 22, 7, 22)
    c.setStrokeColor(colors.black)
    c.line(xs[5], ys[22], xs[5], ys[23])
    words = _amount_words(_number(snapshot.get("total_amount")))
    _draw_left_cell_text(
        c,
        f"Total Amt In Word :- {words} Only.",
        xs[0], ys[23], xs[5] - xs[0], row_h[22], _FONT_BOLD, 8.5,
    )
    _draw_left_cell_text(
        c,
        "Grand Total",
        xs[5], ys[23], xs[7] - xs[5], row_h[22], _FONT_BOLD, 8.5,
        padding=4,
    )
    _draw_left_cell_text(
        c,
        f"₹ {_number(snapshot.get('total_amount')):,.2f}",
        xs[7], ys[23], xs[8] - xs[7], row_h[22], _FONT_BOLD, 8.5,
        padding=3,
    )

    # ------------------------------------------------------------------
    # Bank details / signature, rows 24-30
    # ------------------------------------------------------------------
    rect(0, 23, 3, 29)
    rect(4, 23, 7, 37)
    bank_lines = [
        "BANK DETAILS:-",
        f"Bank name :- {_safe(settings.get('bank_name'))}",
        f"A/C HOLDER :- {_safe(settings.get('account_holder_name') or company_name)}",
        f"ACC NO :- {_safe(settings.get('account_number'))}",
        f"IFSC CODE:- {_safe(settings.get('ifsc_code'))}",
        f"BRANCH:- {_safe(settings.get('branch_name'))}",
    ]
    bank_text = "\n".join(bank_lines)
    bx, by, bw, bh = cell(0, 23, 3, 29)
    _draw_left_cell_text(c, bank_text, bx, by, bw, bh, _FONT_REGULAR, 8.7)

    sx, sy, sw, sh = cell(4, 23, 7, 37)
    signature_text = f"For {company_name}.\n\n\n{_safe(settings.get('owner_name') or 'Proprietor')}"
    _draw_centered_cell_text(c, signature_text, sx, sy, sw, sh, _FONT_REGULAR, 9.5)

    # Declaration rows 31-38.
    rect(0, 30, 3, 37)
    declaration = (
        "‘I/We hereby certify that my/our registration certificate under the "
        "Maharashtra Value Added Tax Act. 2002 is in force on the date on which "
        "the sale of the goods specified in this tax invoice is made by me/us "
        "and that the transaction of sale covered by this tax invoice has been "
        "effected by me/us and it shall be accounted for in the turDECer of sale "
        "while filling of return and the due if any payable on the sale has been paid’."
    )
    dx, dy, dw, dh = cell(0, 30, 3, 37)
    _draw_left_cell_text(c, declaration, dx, dy, dw, dh, _FONT_REGULAR, 7.5, padding=5)

    c.showPage()
    c.save()
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# Amount in words
# ---------------------------------------------------------------------------


def _amount_words(number: float) -> str:
    number = round(float(number or 0), 2)
    rupees = int(number)
    paise = int(round((number - rupees) * 100))

    ones = [
        "Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven",
        "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen",
        "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen",
    ]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    def under_100(n: int) -> str:
        if n < 20:
            return ones[n]
        return tens[n // 10] + (f" {ones[n % 10]}" if n % 10 else "")

    def under_1000(n: int) -> str:
        if n < 100:
            return under_100(n)
        rest = n % 100
        result = f"{ones[n // 100]} Hundred"
        return result + (f" {under_100(rest)}" if rest else "")

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

    result = indian_integer(rupees)
    if paise:
        result += f" and {under_100(paise)} Paise"
    return result


# ---------------------------------------------------------------------------
# Public PDF API
# ---------------------------------------------------------------------------


def build_site_invoice_workbook(
    bill: Any,
    template_path: str | os.PathLike | None = None,
) -> bytes:
    """Compatibility API.

    Historically this returned XLSX bytes. It now returns PDF bytes because
    the runtime no longer needs Excel. New code should call
    generate_site_bill_pdf_from_template().
    """
    snapshot = _load_bill_snapshot(bill)
    settings = _company_values()
    return _draw_invoice(snapshot, settings)


_PDF_CACHE: dict[tuple[Any, ...], bytes] = {}


def _pdf_cache_key(bill: Any, template_path: str | os.PathLike | None = None) -> tuple[Any, ...]:
    bill_id = getattr(bill, "id", None)
    updated = getattr(bill, "updated_at", None)
    template = str(template_path or "reference-template")
    try:
        updated_key = updated.isoformat() if updated else ""
    except AttributeError:
        updated_key = str(updated or "")
    return (bill_id, updated_key, template)


def clear_site_invoice_pdf_cache() -> None:
    _PDF_CACHE.clear()


def xlsx_bytes_to_pdf(xlsx_data: bytes) -> bytes:
    """Deprecated compatibility function.

    Excel conversion is intentionally removed. If bytes are already a PDF,
    return them; otherwise fail clearly so no hidden COM/LibreOffice call can
    reintroduce the old bottleneck.
    """
    if xlsx_data.startswith(b"%PDF"):
        return xlsx_data
    raise RuntimeError(
        "Excel-to-PDF conversion has been removed. "
        "Use generate_site_bill_pdf_from_template() for ReportLab PDF generation."
    )


def generate_site_bill_pdf_from_template(
    bill: Any,
    template_path: str | os.PathLike | None = None,
) -> bytes:
    cache_key = _pdf_cache_key(bill, template_path)
    cached = _PDF_CACHE.get(cache_key)
    if cached is not None:
        return cached

    snapshot = _load_bill_snapshot(bill)
    settings = _company_values()
    pdf_data = _draw_invoice(snapshot, settings)
    _PDF_CACHE[cache_key] = pdf_data

    if len(_PDF_CACHE) > 50:
        oldest_key = next(iter(_PDF_CACHE))
        if oldest_key != cache_key:
            _PDF_CACHE.pop(oldest_key, None)

    return pdf_data
