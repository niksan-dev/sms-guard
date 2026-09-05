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
    path = Path(str(value).replace("\\", "/"))
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
            "site_name": (
                (getattr(site, "name", None) if site else None)
                or (getattr(site, "site_name", None) if site else None)
                or (getattr(site, "site_code", None) if site else None)
                or ""
            ),
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
    """
    Render the Site Bill in the exact visual structure of the supplied
    template_1.xlsx / INV-202609-0002 reference.

    The Excel workbook is used only as a geometry/design reference.
    The final document is generated directly as a one-page A4 PDF.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    page_w, page_h = A4

    # ------------------------------------------------------------------
    # PAGE / GRID
    # ------------------------------------------------------------------
    left = 21.5
    right = 21.5
    top = 18.0
    bottom = 42.0  # leaves room for the small footer below the invoice

    x0 = left
    y_top = page_h - top
    usable_w = page_w - left - right

    # Exact column proportions from the supplied workbook:
    # A:H = 7, 27, 10, 14, 18, 13, 14, 13
    excel_widths = [7, 27, 10, 14, 18, 13, 14, 13]
    scale = usable_w / sum(excel_widths)
    col = [w * scale for w in excel_widths]

    xs = [x0]
    for width in col:
        xs.append(xs[-1] + width)

    # Exact row-height proportions from the supplied workbook.
    excel_heights = [
        24, 48, 27.75, 27.75,
        19.5, 19.5, 19.5, 19.5, 19.5,
        31.5,
        *([24.75] * 13),  # rows 11-23
        15.0, 12.75, 13.5, 12.75, 12.0, 12.0, 15.0,
        12.0, 12.75, 8.25, 15.0, 12.75, 12.0, 9.0, 14.25,
    ]

    grid_h = sum(excel_heights)
    available_h = page_h - top - bottom
    row_scale = available_h / grid_h

    row_h = [h * row_scale for h in excel_heights]
    ys = [y_top]
    for height in row_h:
        ys.append(ys[-1] - height)

    # Reference header fill from the workbook.
    header_fill = colors.HexColor("#D9D2E9")
    border_color = colors.HexColor("#555555")

    def cell(c1: int, r1: int, c2: int | None = None,
             r2: int | None = None):
        if c2 is None:
            c2 = c1
        if r2 is None:
            r2 = r1
        return (
            xs[c1],
            ys[r2 + 1],
            xs[c2 + 1] - xs[c1],
            ys[r1] - ys[r2 + 1],
        )

    def box(c1: int, r1: int, c2: int, r2: int,
            fill=None, line_width=0.55):
        x = xs[c1]
        y = ys[r2 + 1]
        w = xs[c2 + 1] - xs[c1]
        h = ys[r1] - ys[r2 + 1]

        c.setLineWidth(line_width)
        c.setStrokeColor(border_color)

        if fill is not None:
            c.setFillColor(fill)
            c.rect(x, y, w, h, fill=1, stroke=1)
            c.setFillColor(colors.black)
        else:
            c.rect(x, y, w, h, fill=0, stroke=1)

    def vline(ci: int, r1: int, r2: int, width=0.55):
        c.setStrokeColor(border_color)
        c.setLineWidth(width)
        c.line(xs[ci], ys[r1], xs[ci], ys[r2 + 1])

    def hline(r: int, c1: int = 0, c2: int = 7, width=0.55):
        c.setStrokeColor(border_color)
        c.setLineWidth(width)
        c.line(xs[c1], ys[r + 1], xs[c2 + 1], ys[r + 1])

    def right_cell_text(text, x, y, width, height,
                        font=_FONT_REGULAR, size=9.5, padding=5):
        lines = _wrap_text(text, font, size, max(1, width - 2 * padding))
        leading = size * 1.15
        total = len(lines) * leading
        baseline = y + (height + total) / 2 - leading
        c.setFont(font, size)
        for line in lines:
            c.drawRightString(x + width - padding, baseline, line)
            baseline -= leading

    # ------------------------------------------------------------------
    # Outer invoice border
    # ------------------------------------------------------------------
    c.setStrokeColor(border_color)
    c.setLineWidth(0.65)
    c.rect(x0, ys[-1], usable_w, y_top - ys[-1], fill=0, stroke=1)

    # ------------------------------------------------------------------
    # ROW 1 — TAX INVOICE
    # ------------------------------------------------------------------
    box(0, 0, 7, 0)
    x, y, w, h = cell(0, 0, 7, 0)
    c.setFont(_FONT_BOLD, 13)
    c.drawCentredString(x + w / 2, y + h / 2 - 4, "TAX INVOICE")

    # ------------------------------------------------------------------
    # ROWS 2-4 — LOGO + COMPANY HEADER
    # ------------------------------------------------------------------
    box(0, 1, 1, 3)
    box(2, 1, 7, 1)
    box(2, 2, 7, 2)
    box(2, 3, 7, 3)

    logo_x, logo_y, logo_w, logo_h = cell(0, 1, 1, 3)
    logo_path = _resolve_logo_path(settings.get("logo_path"))

    if logo_path:
        try:
            image = ImageReader(str(logo_path))
            iw, ih = image.getSize()
            ratio = min(
                (logo_w - 8) / iw,
                (logo_h - 8) / ih,
            )
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
        str(value).strip()
        for value in (
            settings.get("address"),
            settings.get("city"),
            settings.get("state"),
            settings.get("pincode"),
        )
        if value and str(value).strip()
    )

    contact = " / ".join(
        str(value).strip()
        for value in (
            settings.get("phone"),
            settings.get("email"),
        )
        if value and str(value).strip()
    )

    cx, cy, cw, ch = cell(2, 1, 7, 1)
    _draw_centered_cell_text(
        c, company_name, cx, cy, cw, ch,
        _FONT_BOLD, 17
    )

    # Company name in the reference is blue.
    c.setFillColor(colors.HexColor("#1155CC"))
    _draw_centered_cell_text(
        c, company_name, cx, cy, cw, ch,
        _FONT_BOLD, 17
    )
    c.setFillColor(colors.black)

    cx, cy, cw, ch = cell(2, 2, 7, 2)
    _draw_centered_cell_text(
        c, company_address, cx, cy, cw, ch,
        _FONT_REGULAR, 9.5
    )

    cx, cy, cw, ch = cell(2, 3, 7, 3)
    _draw_centered_cell_text(
        c, contact, cx, cy, cw, ch,
        _FONT_BOLD, 10.5
    )

    # ------------------------------------------------------------------
    # ROWS 5-8 — BILL FROM / BILL TO / INVOICE DETAILS
    # ------------------------------------------------------------------
    box(0, 4, 2, 7)
    box(3, 4, 5, 7)
    box(6, 4, 6, 5)
    box(7, 4, 7, 5)
    box(6, 6, 6, 7)
    box(7, 6, 7, 7)

    bx, by, bw, bh = cell(0, 4, 2, 7)
    _draw_left_cell_text(
        c,
        f"Bill From,\n{company_name}",
        bx, by, bw, bh,
        _FONT_BOLD, 9.5,
    )

    tx, ty, tw, th = cell(3, 4, 5, 7)
    # The reference invoice uses the SITE NAME in the Bill To section.
    # Fall back to customer name only when a site name is unavailable.
    bill_to_name = (
        _safe(snapshot.get("site_name"))
        or _safe(snapshot.get("customer_name"))
    )
    _draw_left_cell_text(
        c,
        f"Bill To,\n{bill_to_name}",
        tx, ty, tw, th,
        _FONT_BOLD, 9.5,
    )

    gx, gy, gw, gh = cell(6, 4, 6, 5)
    _draw_left_cell_text(
        c, "Invoice\nNo.",
        gx, gy, gw, gh,
        _FONT_BOLD, 9.5,
    )

    hx, hy, hw, hh = cell(7, 4, 7, 5)
    _draw_centered_cell_text(
        c, snapshot.get("bill_number"),
        hx, hy, hw, hh,
        _FONT_REGULAR, 9.2,
    )

    gx, gy, gw, gh = cell(6, 6, 6, 7)
    _draw_left_cell_text(
        c, "Invoice\nDate",
        gx, gy, gw, gh,
        _FONT_BOLD, 9.5,
    )

    hx, hy, hw, hh = cell(7, 6, 7, 7)
    _draw_centered_cell_text(
        c,
        _date_text(snapshot.get("bill_date") or date.today()),
        hx, hy, hw, hh,
        _FONT_REGULAR, 9.2,
    )

    # ------------------------------------------------------------------
    # ROW 9 — PAN
    # ------------------------------------------------------------------
    box(0, 8, 2, 8)
    box(3, 8, 5, 8)
    box(6, 8, 7, 8)

    px, py, pw, ph = cell(0, 8, 2, 8)
    company_pan = _safe(settings.get("pan_number"))
    _draw_left_cell_text(
        c,
        f"PAN:- {company_pan}" if company_pan else "PAN:-",
        px, py, pw, ph,
        _FONT_REGULAR, 9.5,
    )

    cx, cy, cw, ch = cell(3, 8, 5, 8)
    customer_pan = _safe(snapshot.get("customer_pan"))
    _draw_left_cell_text(
        c,
        f"PAN:- {customer_pan}" if customer_pan else "PAN:-",
        cx, cy, cw, ch,
        _FONT_REGULAR, 9.5,
    )

    # ------------------------------------------------------------------
    # ROW 10 — SITE ADDRESS
    # ------------------------------------------------------------------
    box(0, 9, 7, 9)
    ax, ay, aw, ah = cell(0, 9, 7, 9)
    _draw_left_cell_text(
        c,
        f"Site Address:- {_safe(snapshot.get('site_address'))}",
        ax, ay, aw, ah,
        _FONT_REGULAR, 9.2,
    )

    # ------------------------------------------------------------------
    # ROW 11 — TABLE HEADER
    # ------------------------------------------------------------------
    box(0, 10, 4, 10, fill=header_fill)
    box(5, 10, 7, 10, fill=header_fill)

    # F11:H11 is merged; E is "No. Of Days".
    # Draw the vertical separators A|B|C|D|E|F:H.
    for ci in range(1, 6):
        vline(ci, 10, 10)

    headers = [
        ("Sr.\nNo.", 0),
        ("PARTICULARS", 1),
        ("UNIT", 2),
        ("QUANTITY", 3),
        ("No. Of Days", 4),
    ]

    for label, ci in headers:
        cx, cy, cw, ch = cell(ci, 10)
        _draw_centered_cell_text(
            c, label, cx, cy, cw, ch,
            _FONT_BOLD, 9.5
        )

    cx, cy, cw, ch = cell(5, 10, 7, 10)
    _draw_centered_cell_text(
        c, "AMOUNT",
        cx, cy, cw, ch,
        _FONT_BOLD, 9.5
    )

    # ------------------------------------------------------------------
    # ROW 12 — SECTION TITLE
    # ------------------------------------------------------------------
    box(0, 11, 0, 11)
    box(1, 11, 7, 11)

    cx, cy, cw, ch = cell(0, 11)
    _draw_centered_cell_text(
        c, "A", cx, cy, cw, ch,
        _FONT_BOLD, 9.5
    )

    cx, cy, cw, ch = cell(1, 11, 7, 11)
    _draw_left_cell_text(
        c, "Providing Security Guard",
        cx, cy, cw, ch,
        _FONT_BOLD, 9.5,
    )

    # ------------------------------------------------------------------
    # ROWS 13-14 — MONTH SECTION
    # ------------------------------------------------------------------
    # The reference template has A13:A14 and B13:B14 merged vertically.
    # C/D/E remain separate columns, while F:H is the merged AMOUNT area.
    # Do NOT draw the individual row boxes first: doing so creates a
    # horizontal line through the merged month cell.

    # Outer/merged cells.
    box(0, 12, 0, 13)
    box(1, 12, 1, 13)

    # C, D and E are separate cells on both rows.
    for r in (12, 13):
        box(2, r, 2, r)
        box(3, r, 3, r)
        box(4, r, 4, r)
        # F:H is one merged amount cell for each row.
        box(5, r, 7, r)

    # The merged cells above already provide their vertical boundaries.
    # Explicitly reinforce only the column boundaries that continue through
    # the two rows.  There must be NO G/H internal lines inside AMOUNT.
    for ci in (2, 3, 4, 5):
        vline(ci, 12, 13)

    # Keep the month number and text vertically centred in their merged cells.
    cx, cy, cw, ch = cell(0, 12, 0, 13)
    _draw_centered_cell_text(
        c, "1", cx, cy, cw, ch,
        _FONT_REGULAR, 9.5
    )

    month_text = (
        f"For the month of\n"
        f"{_month_text(snapshot['billing_year'], snapshot['billing_month'])}"
    )

    cx, cy, cw, ch = cell(1, 12, 1, 13)
    _draw_left_cell_text(
        c, month_text, cx, cy, cw, ch,
        _FONT_REGULAR, 9.0, padding=5
    )

    # ------------------------------------------------------------------
    # ROWS 15-19 — SHIFT LINES
    # ------------------------------------------------------------------
    shift_rows = [
        (14, "Day/Night", snapshot.get("shift_1_count", 0)),
        (15, "Day/Night", snapshot.get("shift_2_count", 0)),
    ]

    shift_rate = _number(snapshot.get("shift_rate"))
    total_days = int(snapshot.get("total_days") or 0)

    # Draw each row as A|B|C|D|E|F:H.  F:H must stay merged.
    for r in range(14, 19):
        box(0, r, 0, r)
        box(1, r, 1, r)
        box(2, r, 2, r)
        box(3, r, 3, r)
        box(4, r, 4, r)
        box(5, r, 7, r)

    for r, unit, quantity in shift_rows:
        quantity = int(quantity or 0)

        values = {
            0: "",
            1: unit,
            2: "01",
            3: f"{quantity:02d}",
            4: str(total_days),
        }

        for ci, value in values.items():
            cx, cy, cw, ch = cell(ci, r)
            _draw_centered_cell_text(
                c, value, cx, cy, cw, ch,
                _FONT_REGULAR, 9.5
            )

        amount = shift_rate * quantity
        cx, cy, cw, ch = cell(5, r, 7, r)
        right_cell_text(
            f"₹ {amount:,.2f}",
            cx, cy, cw, ch,
            _FONT_REGULAR, 9.5, padding=5
        )

    # ------------------------------------------------------------------
    # ROWS 20-22 — TOTALS
    # ------------------------------------------------------------------
    gross = _number(snapshot.get("gross_amount"))
    cgst = _number(snapshot.get("cgst_amount"))
    sgst = _number(snapshot.get("sgst_amount"))

    cgst_rate = _number(settings.get("cgst_rate", 9.0))
    sgst_rate = _number(settings.get("sgst_rate", 9.0))

    total_rows = [
        (19, "Gross Bill Amt.", gross, True),
        (20, f"Add : CGST @ {cgst_rate:.1f} % Of Gross", cgst, False),
        (21, f"Add : SGST @ {sgst_rate:.1f} % Of Gross", sgst, False),
    ]

    for r, label, amount, bold in total_rows:
        box(0, r, 4, r)
        box(5, r, 7, r)

        lx, ly, lw, lh = cell(0, r, 4, r)
        right_cell_text(
            label,
            lx, ly, lw, lh,
            _FONT_BOLD if bold else _FONT_REGULAR,
            9.5,
            padding=5,
        )

        ax, ay, aw, ah = cell(5, r, 7, r)
        right_cell_text(
            f"₹ {amount:,.2f}" if amount else "0",
            ax, ay, aw, ah,
            _FONT_BOLD if bold else _FONT_REGULAR,
            9.5,
            padding=5,
        )

    # ------------------------------------------------------------------
    # ROW 23 — AMOUNT IN WORDS + GRAND TOTAL
    # ------------------------------------------------------------------
    box(0, 22, 4, 22)
    box(5, 22, 5, 22)
    box(6, 22, 7, 22)

    words = _amount_words(_number(snapshot.get("total_amount")))

    wx, wy, ww, wh = cell(0, 22, 4, 22)
    _draw_left_cell_text(
        c,
        f"Total Amt In Word :- {words} Only.",
        wx, wy, ww, wh,
        _FONT_BOLD, 8.5, padding=5
    )

    gx, gy, gw, gh = cell(5, 22, 5, 22)
    _draw_left_cell_text(
        c,
        "Grand Total.",
        gx, gy, gw, gh,
        _FONT_BOLD, 8.5, padding=4
    )

    ax, ay, aw, ah = cell(6, 22, 7, 22)
    right_cell_text(
        f"₹ {_number(snapshot.get('total_amount')):,.2f}",
        ax, ay, aw, ah,
        _FONT_BOLD, 8.5, padding=4
    )

    # ------------------------------------------------------------------
    # ROWS 24-30 — BANK DETAILS
    # ROWS 24-38 — SIGNATURE
    # ROWS 31-38 — DECLARATION
    # ------------------------------------------------------------------
    box(0, 23, 3, 29)
    box(4, 23, 7, 37)
    box(0, 30, 3, 37)

    bank_lines = [
        "BANK DETAILS:-",
        f"Bank name :- {_safe(settings.get('bank_name'))}",
        (
            "A/C HOLDER :- "
            f"{_safe(settings.get('account_holder_name') or company_name)}"
        ),
        f"ACC NO :- {_safe(settings.get('account_number'))}",
        f"IFSC CODE:- {_safe(settings.get('ifsc_code'))}",
        f"BRANCH:- {_safe(settings.get('branch_name'))}",
    ]

    bx, by, bw, bh = cell(0, 23, 3, 29)
    # Draw bank details as explicit lines to match the compact reference.
    c.setFont(_FONT_REGULAR, 8.7)
    line_y = by + bh - 12
    for line in bank_lines:
        c.drawString(bx + 5, line_y, line)
        line_y -= 11.5

    sx, sy, sw, sh = cell(4, 23, 7, 37)
    signature_text = (
        f"For {company_name}.\n\n\n"
        f"{_safe(settings.get('owner_name') or 'Proprietor')}"
    )
    _draw_centered_cell_text(
        c,
        signature_text,
        sx, sy, sw, sh,
        _FONT_REGULAR, 9.5
    )

    declaration = (
        "‘I/We hereby certify that my/our registration certificate under the "
        "Maharashtra Value Added Tax Act. 2002 is in force on the date on "
        "which the sale of the goods specified in this tax invoice is made "
        "by me/us and that the transaction of sale covered by this tax "
        "invoice has been effected by me/us and it shall be accounted for "
        "in the turDECer of sale while filling of return and the due if any "
        "payable on the sale has been paid’."
    )

    dx, dy, dw, dh = cell(0, 30, 3, 37)
    _draw_left_cell_text(
        c,
        declaration,
        dx, dy, dw, dh,
        _FONT_REGULAR, 7.5, padding=5
    )

    # ------------------------------------------------------------------
    # FOOTER — matches the supplied reference PDF
    # ------------------------------------------------------------------
    c.setFont(_FONT_REGULAR, 7.5)
    c.setFillColor(colors.HexColor("#444444"))
    c.drawCentredString(
        page_w / 2,
        17,
        company_name,
    )
    c.setFillColor(colors.black)

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
