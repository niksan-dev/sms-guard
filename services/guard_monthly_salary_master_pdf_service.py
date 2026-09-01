"""
Direct PDF generation for Monthly Salary Master.

This intentionally does NOT use Excel/LibreOffice.

The PDF is generated directly with ReportLab for fast export.

Features:
    - One guard per row
    - Dynamic advance categories
    - Indian Rupee symbol (₹)
    - Unicode DejaVu font
    - Landscape A4
    - Automatic column scaling
    - Totals row
    - Summary section
"""

from __future__ import annotations

import io
from datetime import date
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import (
    TA_CENTER,
    TA_LEFT,
    TA_RIGHT,
)
from reportlab.lib.pagesizes import (
    A4,
    landscape,
)
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = (
    Path(__file__).resolve().parents[1]
)

FONT_DIR = (
    PROJECT_ROOT / "fonts"
)


# ============================================================
# UNICODE FONTS
#
# DejaVu Sans supports the Indian Rupee symbol ₹.
# ============================================================

DEJAVU_REGULAR = (
    FONT_DIR / "DejaVuSans.ttf"
)

DEJAVU_BOLD = (
    FONT_DIR / "DejaVuSans-Bold.ttf"
)


def _register_fonts() -> None:
    """
    Register Unicode fonts used by the PDF.

    The font files must exist inside:

        <project>/fonts/

    Required:
        DejaVuSans.ttf
        DejaVuSans-Bold.ttf
    """

    if not DEJAVU_REGULAR.exists():

        raise FileNotFoundError(
            "DejaVuSans.ttf not found.\n\n"
            f"Expected location:\n"
            f"{DEJAVU_REGULAR}\n\n"
            "Please place DejaVuSans.ttf inside the "
            "project fonts folder."
        )

    if not DEJAVU_BOLD.exists():

        raise FileNotFoundError(
            "DejaVuSans-Bold.ttf not found.\n\n"
            f"Expected location:\n"
            f"{DEJAVU_BOLD}\n\n"
            "Please place DejaVuSans-Bold.ttf inside the "
            "project fonts folder."
        )

    # Register only once.
    if "DejaVuSans" not in pdfmetrics.getRegisteredFontNames():

        pdfmetrics.registerFont(
            TTFont(
                "DejaVuSans",
                str(DEJAVU_REGULAR),
            )
        )

    if (
        "DejaVuSans-Bold"
        not in pdfmetrics.getRegisteredFontNames()
    ):

        pdfmetrics.registerFont(
            TTFont(
                "DejaVuSans-Bold",
                str(DEJAVU_BOLD),
            )
        )


# Register fonts when this module is imported.
_register_fonts()


# ============================================================
# HELPERS
# ============================================================

def _money(value: Any) -> str:
    """
    Format an amount using the Indian Rupee symbol.

    Example:
        4435.48 -> ₹4,435.48
    """

    try:

        return (
            f"₹{float(value or 0):,.2f}"
        )

    except (
        TypeError,
        ValueError,
    ):

        return "₹0.00"


def _number(value: Any) -> float:

    try:

        return float(
            value or 0
        )

    except (
        TypeError,
        ValueError,
    ):

        return 0.0


def _month_name(
    year: int,
    month: int,
) -> str:

    return date(
        int(year),
        int(month),
        1,
    ).strftime(
        "%B %Y"
    )


def _safe_text(
    value: Any,
) -> str:

    if value is None:

        return ""

    return str(
        value
    ).strip()


# ============================================================
# PDF GENERATOR
# ============================================================

def generate_monthly_salary_master_pdf(
    master: dict[str, Any],
) -> bytes:
    """
    Generate Monthly Salary Master PDF directly
    using ReportLab.

    No Excel.
    No LibreOffice.
    No XLSX conversion.

    Parameters
    ----------
    master:
        Output returned by:

            get_monthly_salary_master()

    Returns
    -------
    bytes
        Generated PDF bytes.
    """

    # ========================================================
    # OUTPUT
    # ========================================================

    output = io.BytesIO()

    # ========================================================
    # PAGE
    # ========================================================

    document = SimpleDocTemplate(
        output,

        pagesize=landscape(A4),

        rightMargin=8 * mm,
        leftMargin=8 * mm,
        topMargin=8 * mm,
        bottomMargin=8 * mm,

        title=(
            "Monthly Salary Master - "
            f"{master.get('month_name', '')}"
        ),

        author=(
            "Security Management System"
        ),
    )

    # ========================================================
    # STYLES
    #
    # IMPORTANT:
    # Every style uses DejaVu.
    #
    # This is what allows ₹ to render correctly.
    # ========================================================

    styles = getSampleStyleSheet()

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    title_style = ParagraphStyle(
        "SalaryMasterTitle",

        parent=styles["Title"],

        fontName="DejaVuSans-Bold",

        fontSize=16,

        leading=19,

        alignment=TA_CENTER,

        spaceAfter=2 * mm,
    )

    # --------------------------------------------------------
    # SUBTITLE
    # --------------------------------------------------------

    subtitle_style = ParagraphStyle(
        "SalaryMasterSubtitle",

        parent=styles["Normal"],

        fontName="DejaVuSans",

        fontSize=9,

        leading=11,

        alignment=TA_CENTER,

        spaceAfter=5 * mm,
    )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    header_style = ParagraphStyle(
        "SalaryMasterHeader",

        parent=styles["Normal"],

        fontName="DejaVuSans-Bold",

        fontSize=7.5,

        leading=9,

        alignment=TA_CENTER,
    )

    # --------------------------------------------------------
    # NORMAL CELL
    # --------------------------------------------------------

    cell_style = ParagraphStyle(
        "SalaryMasterCell",

        parent=styles["Normal"],

        fontName="DejaVuSans",

        fontSize=7.5,

        leading=9,

        alignment=TA_LEFT,
    )

    # --------------------------------------------------------
    # CENTER CELL
    # --------------------------------------------------------

    cell_center_style = ParagraphStyle(
        "SalaryMasterCellCenter",

        parent=cell_style,

        fontName="DejaVuSans",

        alignment=TA_CENTER,
    )

    # --------------------------------------------------------
    # RIGHT / MONEY CELL
    # --------------------------------------------------------

    cell_right_style = ParagraphStyle(
        "SalaryMasterCellRight",

        parent=cell_style,

        fontName="DejaVuSans",

        alignment=TA_RIGHT,
    )

    # --------------------------------------------------------
    # TOTAL
    # --------------------------------------------------------

    total_style = ParagraphStyle(
        "SalaryMasterTotal",

        parent=styles["Normal"],

        fontName="DejaVuSans-Bold",

        fontSize=7.5,

        leading=9,

        alignment=TA_RIGHT,
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary_style = ParagraphStyle(
        "SalaryMasterSummary",

        parent=styles["Normal"],

        fontName="DejaVuSans-Bold",

        fontSize=8,

        leading=10,

        alignment=TA_RIGHT,
    )

    story = []

    # ========================================================
    # TITLE
    # ========================================================

    month_name = _safe_text(
        master.get(
            "month_name",
            "",
        )
    )

    story.append(
        Paragraph(
            "MONTHLY SALARY MASTER",
            title_style,
        )
    )

    story.append(
        Paragraph(
            month_name,
            subtitle_style,
        )
    )

    # ========================================================
    # COLUMNS
    # ========================================================

    advance_categories = list(
        master.get(
            "advance_categories",
            [],
        )
    )

    columns = [
    "Guard ID",
    "Guard Name",
    "Monthly Salary",
    "Shift 1",
    "Shift 2",
    "Total Shifts",
]

    # --------------------------------------------------------
    # Dynamic advance columns
    # --------------------------------------------------------

    for category in advance_categories:

        columns.append(
            _safe_text(category)
        )

    # --------------------------------------------------------
    # Final salary columns
    # --------------------------------------------------------

    columns.extend([
        "Earned",
        "Net Payable",
    ])

    # ========================================================
    # HEADER ROW
    # ========================================================

    table_data = [

        [
            Paragraph(
                str(column),
                header_style,
            )

            for column in columns
        ]

    ]

    # ========================================================
    # GUARD ROWS
    # ========================================================

    rows = master.get(
        "rows",
        [],
    )

    for row in rows:

        # ----------------------------------------------------
        # BASIC INFORMATION
        # ----------------------------------------------------

        table_row = [

            Paragraph(
                _safe_text(
                    row.get(
                        "employee_id",
                        "",
                    )
                ),
                cell_center_style,
            ),

            Paragraph(
                _safe_text(
                    row.get(
                        "guard_name",
                        "",
                    )
                ),
                cell_style,
            ),

            Paragraph(
                _money(
                    row.get(
                        "monthly_salary",
                        0.0,
                    )
                ),
                cell_right_style,
            ),

            Paragraph(
                str(
                    row.get(
                        "shift_1",
                        0,
                    )
                ),
                cell_center_style,
            ),

            Paragraph(
                str(
                    row.get(
                        "shift_2",
                        0,
                    )
                ),
                cell_center_style,
            ),

            Paragraph(
                str(
                    row.get(
                        "total_shifts",
                        0,
                    )
                ),
                cell_center_style,
            ),

        ]

        # ----------------------------------------------------
        # ADVANCE CATEGORIES
        # ----------------------------------------------------

        for category in advance_categories:

            amount = row.get(
                f"advance_{category}",
                0.0,
            )

            table_row.append(

                Paragraph(
                    _money(amount),
                    cell_right_style,
                )

            )

        # ----------------------------------------------------
        # EARNED
        # ----------------------------------------------------

        earned = row.get(
            "earned",
            0.0,
        )

        table_row.append(

            Paragraph(
                _money(earned),
                cell_right_style,
            )

        )

        # ----------------------------------------------------
        # NET PAYABLE
        # ----------------------------------------------------

        net_payable = row.get(
            "net_payable",
            0.0,
        )

        table_row.append(

            Paragraph(
                _money(net_payable),
                cell_right_style,
            )

        )

        table_data.append(
            table_row
        )

    # ========================================================
    # TOTAL ROW
    # ========================================================

    totals = master.get(
        "totals",
        {}
    )

    total_row = []

    # --------------------------------------------------------
    # TOTAL LABEL
    # --------------------------------------------------------

    total_row.append(

        Paragraph(
            "TOTAL",
            total_style,
        )

    )

    # Guard name column
    total_row.append("")
    total_row.append("")

    # --------------------------------------------------------
    # SHIFT 1 TOTAL
    # --------------------------------------------------------

    total_row.append(

        Paragraph(
            str(
                totals.get(
                    "shift_1",
                    0,
                )
            ),
            total_style,
        )

    )

    # --------------------------------------------------------
    # SHIFT 2 TOTAL
    # --------------------------------------------------------

    total_row.append(

        Paragraph(
            str(
                totals.get(
                    "shift_2",
                    0,
                )
            ),
            total_style,
        )

    )

    # --------------------------------------------------------
    # TOTAL SHIFTS
    # --------------------------------------------------------

    total_row.append(

        Paragraph(
            str(
                totals.get(
                    "total_shifts",
                    0,
                )
            ),
            total_style,
        )

    )

    # ========================================================
    # ADVANCE TOTALS
    # ========================================================

    category_totals = totals.get(
        "advance_categories",
        {}
    )

    for category in advance_categories:

        category_total = (
            category_totals.get(
                category,
                0.0,
            )
        )

        total_row.append(

            Paragraph(
                _money(category_total),
                total_style,
            )

        )

    # ========================================================
    # EARNED TOTAL
    # ========================================================

    total_row.append(

        Paragraph(
            _money(
                totals.get(
                    "earned",
                    0.0,
                )
            ),
            total_style,
        )

    )

    # ========================================================
    # NET PAYABLE TOTAL
    # ========================================================

    total_row.append(

        Paragraph(
            _money(
                totals.get(
                    "net_payable",
                    0.0,
                )
            ),
            total_style,
        )

    )

    table_data.append(
        total_row
    )

    # ========================================================
    # COLUMN WIDTHS
    # ========================================================

    page_width = landscape(A4)[0]

    usable_width = (
        page_width
        - (16 * mm)
    )

    # --------------------------------------------------------
    # Base columns
    # --------------------------------------------------------

    widths = [
    25 * mm,   # Guard ID
    42 * mm,   # Guard Name
    30 * mm,   # Monthly Salary
    20 * mm,   # Shift 1
    20 * mm,   # Shift 2
    25 * mm,   # Total Shifts
]

    # --------------------------------------------------------
    # Dynamic advance columns
    # --------------------------------------------------------

    advance_width = 25 * mm

    widths.extend(

        [
            advance_width
            for _ in advance_categories
        ]

    )

    # --------------------------------------------------------
    # Salary columns
    # --------------------------------------------------------

    widths.extend([

        31 * mm,   # Earned

        34 * mm,   # Net Payable

    ])

    # ========================================================
    # SCALE TABLE IF NECESSARY
    # ========================================================

    total_width = sum(
        widths
    )

    if total_width > usable_width:

        scale = (
            usable_width
            / total_width
        )

        widths = [

            width * scale

            for width in widths

        ]

    # ========================================================
    # TABLE
    # ========================================================

    table = Table(

        table_data,

        colWidths=widths,

        repeatRows=1,

        hAlign="CENTER",

    )

    # ========================================================
    # TABLE STYLE
    # ========================================================

    table.setStyle(

        TableStyle([

            # ------------------------------------------------
            # HEADER BACKGROUND
            # ------------------------------------------------

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor(
                    "#E9ECEF"
                ),
            ),

            # ------------------------------------------------
            # HEADER TEXT
            # ------------------------------------------------

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.black,
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "DejaVuSans-Bold",
            ),

            # ------------------------------------------------
            # HEADER ALIGNMENT
            # ------------------------------------------------

            (
                "ALIGN",
                (0, 0),
                (-1, 0),
                "CENTER",
            ),

            # ------------------------------------------------
            # VERTICAL ALIGNMENT
            # ------------------------------------------------

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),

            # ------------------------------------------------
            # GRID
            # ------------------------------------------------

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black,
            ),

            # ------------------------------------------------
            # PADDING
            # ------------------------------------------------

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                3,
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                3,
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                4,
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                4,
            ),

            # ------------------------------------------------
            # TOTAL ROW BACKGROUND
            # ------------------------------------------------

            (
                "BACKGROUND",
                (0, -1),
                (-1, -1),
                colors.HexColor(
                    "#E9ECEF"
                ),
            ),

            # ------------------------------------------------
            # TOTAL ROW FONT
            # ------------------------------------------------

            (
                "FONTNAME",
                (0, -1),
                (-1, -1),
                "DejaVuSans-Bold",
            ),

            # ------------------------------------------------
            # TOTAL ROW BORDER
            # ------------------------------------------------

            (
                "LINEABOVE",
                (0, -1),
                (-1, -1),
                1,
                colors.black,
            ),

        ])

    )

    story.append(
        table
    )

    # ========================================================
    # SPACE BEFORE SUMMARY
    # ========================================================

    story.append(

        Spacer(
            1,
            5 * mm
        )

    )

    # ========================================================
    # SUMMARY
    # ========================================================

    summary_text = (

        f"Total Guards: "
        f"{master.get('guard_count', 0)}"

        f"    |    "

        f"Total Advances: "
        f"{_money(totals.get('advances', 0))}"

        f"    |    "

        f"Total Earned: "
        f"{_money(totals.get('earned', 0))}"

        f"    |    "

        f"Total Net Payable: "
        f"{_money(totals.get('net_payable', 0))}"

    )

    story.append(

        Paragraph(
            summary_text,
            summary_style,
        )

    )

    # ========================================================
    # BUILD PDF
    # ========================================================

    document.build(
        story
    )

    # ========================================================
    # RETURN PDF BYTES
    # ========================================================

    return output.getvalue()