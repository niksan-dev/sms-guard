from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)


# ============================================================
# HELPERS
# ============================================================

def money(value):
    return f"₹ {float(value or 0):,.2f}"


def month_name(month):
    return datetime(
        2000,
        int(month),
        1
    ).strftime("%B")


def amount_in_words(amount):
    """
    Basic Indian currency amount in words.
    """

    amount = round(float(amount or 0), 2)

    rupees = int(amount)
    paise = int(round((amount - rupees) * 100))

    ones = [
        "",
        "One",
        "Two",
        "Three",
        "Four",
        "Five",
        "Six",
        "Seven",
        "Eight",
        "Nine",
        "Ten",
        "Eleven",
        "Twelve",
        "Thirteen",
        "Fourteen",
        "Fifteen",
        "Sixteen",
        "Seventeen",
        "Eighteen",
        "Nineteen",
    ]

    tens = [
        "",
        "",
        "Twenty",
        "Thirty",
        "Forty",
        "Fifty",
        "Sixty",
        "Seventy",
        "Eighty",
        "Ninety",
    ]

    def under_100(n):

        if n < 20:
            return ones[n]

        return (
            tens[n // 10]
            + (
                " " + ones[n % 10]
                if n % 10
                else ""
            )
        )

    def under_1000(n):

        if n < 100:
            return under_100(n)

        return (
            ones[n // 100]
            + " Hundred"
            + (
                " " + under_100(n % 100)
                if n % 100
                else ""
            )
        )

    def indian_words(n):

        if n == 0:
            return "Zero"

        parts = []

        crore = n // 10_000_000
        n %= 10_000_000

        lakh = n // 100_000
        n %= 100_000

        thousand = n // 1_000
        n %= 1_000

        if crore:
            parts.append(
                under_100(crore)
                + " Crore"
            )

        if lakh:
            parts.append(
                under_100(lakh)
                + " Lakh"
            )

        if thousand:
            parts.append(
                under_100(thousand)
                + " Thousand"
            )

        if n:
            parts.append(
                under_1000(n)
            )

        return " ".join(parts)

    result = indian_words(rupees)

    if paise:
        result += (
            f" and {indian_words(paise)} Paise"
        )

    return result + " Only"


# ============================================================
# COMMON STYLES
# ============================================================

def get_styles():

    styles = getSampleStyleSheet()

    return {

        "company": ParagraphStyle(
            "Company",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=3,
        ),

        "title": ParagraphStyle(
            "Title",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),

        "normal": ParagraphStyle(
            "NormalCustom",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
        ),

        "small": ParagraphStyle(
            "Small",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
        ),

        "right": ParagraphStyle(
            "Right",
            parent=styles["Normal"],
            fontSize=9,
            alignment=TA_RIGHT,
        ),
    }


# ============================================================
# GUARD SALARY SLIP PDF
# ============================================================

def generate_guard_salary_pdf(data):

    buffer = BytesIO()

    styles = get_styles()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="Guard Salary Slip",
    )

    story = []

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "AADHAR SECURITY SERVICES",
            styles["company"]
        )
    )

    story.append(
        Paragraph(
            "GUARD SALARY SLIP",
            styles["title"]
        )
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.black
        )
    )

    story.append(Spacer(1, 6))

    # --------------------------------------------------------
    # BASIC DETAILS
    # --------------------------------------------------------

    details = [
        [
            Paragraph("<b>Slip No.</b>", styles["normal"]),
            data.get("slip_number", "-"),
            Paragraph("<b>Salary Month</b>", styles["normal"]),
            f"{month_name(data['salary_month'])} "
            f"{data['salary_year']}",
        ],
        [
            Paragraph("<b>Employee ID</b>", styles["normal"]),
            data.get("employee_id", "-"),
            Paragraph("<b>Guard Name</b>", styles["normal"]),
            data.get("guard_name", "-"),
        ],
    ]

    table = Table(
        details,
        colWidths=[
            30 * mm,
            50 * mm,
            35 * mm,
            55 * mm,
        ]
    )

    table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
            ("BACKGROUND", (2, 0), (2, -1), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])
    )

    story.append(table)

    story.append(Spacer(1, 10))

    # --------------------------------------------------------
    # EARNINGS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "<b>EARNINGS</b>",
            styles["normal"]
        )
    )

    earnings = [

        ["Description", "Value"],

        [
            "Days in Month",
            str(data.get("total_days", 0))
        ],

        [
            "Present Days",
            str(data.get("present_days", 0))
        ],

        [
            "Shift 1",
            str(data.get("shift_1_count", 0))
        ],

        [
            "Shift 2",
            str(data.get("shift_2_count", 0))
        ],

        [
            "Total Shifts",
            str(data.get("total_shifts", 0))
        ],

        [
            "Monthly Salary",
            money(data.get("monthly_salary", 0))
        ],

        [
            "Salary Per Shift",
            money(data.get("shift_rate", 0))
        ],

        [
            "Gross Salary",
            money(data.get("gross_salary", 0))
        ],
    ]

    earnings_table = Table(
        earnings,
        colWidths=[
            125 * mm,
            45 * mm,
        ]
    )

    earnings_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 1), (1, -1), "RIGHT"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])
    )

    story.append(earnings_table)

    story.append(Spacer(1, 10))

    # --------------------------------------------------------
    # ADVANCES
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "<b>ADVANCES / DEDUCTIONS</b>",
            styles["normal"]
        )
    )

    advance_rows = [
        [
            "Date",
            "Category",
            "Description",
            "Amount",
        ]
    ]

    for advance in data.get("advances", []):

        advance_rows.append([
            str(advance.record_date),
            advance.category or "-",
            advance.description or "-",
            money(advance.amount),
        ])

    if len(advance_rows) == 1:

        advance_rows.append([
            "-",
            "No advances",
            "-",
            money(0),
        ])

    advance_rows.append([
        "",
        "",
        "TOTAL ADVANCE",
        money(data.get("total_advance", 0)),
    ])

    advance_table = Table(
        advance_rows,
        colWidths=[
            28 * mm,
            38 * mm,
            70 * mm,
            34 * mm,
        ]
    )

    advance_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            (
                "FONTNAME",
                (0, -1),
                (-1, -1),
                "Helvetica-Bold"
            ),
            ("ALIGN", (3, 1), (3, -1), "RIGHT"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])
    )

    story.append(advance_table)

    story.append(Spacer(1, 12))

    # --------------------------------------------------------
    # NET PAYABLE
    # --------------------------------------------------------

    net_table = Table(
        [
            [
                Paragraph(
                    "<b>GROSS SALARY</b>",
                    styles["normal"]
                ),
                money(data.get("gross_salary", 0)),
            ],
            [
                Paragraph(
                    "<b>LESS: TOTAL ADVANCE</b>",
                    styles["normal"]
                ),
                money(data.get("total_advance", 0)),
            ],
            [
                Paragraph(
                    "<b>NET PAYABLE</b>",
                    styles["normal"]
                ),
                Paragraph(
                    f"<b>{money(data.get('net_payable', 0))}</b>",
                    styles["right"]
                ),
            ],
        ],
        colWidths=[
            125 * mm,
            45 * mm,
        ]
    )

    net_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.7, colors.black),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("BACKGROUND", (0, 2), (-1, 2), colors.lightgrey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ])
    )

    story.append(net_table)

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            "<b>Amount in Words:</b> "
            + amount_in_words(
                data.get("net_payable", 0)
            ),
            styles["normal"]
        )
    )

    story.append(Spacer(1, 25))

    signature = Table(
        [
            [
                "Employee Signature",
                "Authorized Signature",
            ]
        ],
        colWidths=[
            85 * mm,
            85 * mm,
        ]
    )

    signature.setStyle(
        TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("LINEABOVE", (0, 0), (-1, 0), 0.5, colors.black),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
        ])
    )

    story.append(signature)

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# SITE BILL PDF
# ============================================================

def generate_site_bill_pdf(data):

    buffer = BytesIO()

    styles = get_styles()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="Site Bill",
    )

    story = []

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "AADHAR SECURITY SERVICES",
            styles["company"]
        )
    )

    story.append(
        Paragraph(
            "SECURITY SERVICES BILL",
            styles["title"]
        )
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.black
        )
    )

    story.append(Spacer(1, 8))

    # --------------------------------------------------------
    # BILL DETAILS
    # --------------------------------------------------------

    details = [
        [
            Paragraph("<b>Invoice No.</b>", styles["normal"]),
            data.get("bill_number", "-"),
            Paragraph("<b>Invoice Date</b>", styles["normal"]),
            datetime.now().strftime("%d-%m-%Y"),
        ],
        [
            Paragraph("<b>Billing Month</b>", styles["normal"]),
            f"{month_name(data['billing_month'])} "
            f"{data['billing_year']}",
            Paragraph("<b>Site Code</b>", styles["normal"]),
            data.get("site_code", "-"),
        ],
        [
            Paragraph("<b>Site Name</b>", styles["normal"]),
            data.get("site_name", "-"),
            "",
            "",
        ],
    ]

    details_table = Table(
        details,
        colWidths=[
            30 * mm,
            55 * mm,
            35 * mm,
            50 * mm,
        ]
    )

    details_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
            ("BACKGROUND", (2, 0), (2, 1), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("SPAN", (1, 2), (3, 2)),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])
    )

    story.append(details_table)

    story.append(Spacer(1, 12))

    # --------------------------------------------------------
    # BILL TABLE
    # --------------------------------------------------------

    bill_rows = [
        [
            "Particular",
            "Shift",
            "Guards",
            "Days",
            "Rate",
            "Amount",
        ]
    ]

    shift_rate = float(
        data.get("shift_rate", 0)
    )

    total_days = data.get(
        "total_days",
        0
    )

    shift_1 = int(
        data.get("shift_1_count", 0)
    )

    shift_2 = int(
        data.get("shift_2_count", 0)
    )

    if shift_1 > 0:

        amount = shift_rate * shift_1

        bill_rows.append([
            "Security Guard Service",
            "Shift 1",
            str(shift_1),
            str(total_days),
            money(shift_rate),
            money(amount),
        ])

    if shift_2 > 0:

        amount = shift_rate * shift_2

        bill_rows.append([
            "Security Guard Service",
            "Shift 2",
            str(shift_2),
            str(total_days),
            money(shift_rate),
            money(amount),
        ])

    if shift_1 == 0 and shift_2 == 0:

        bill_rows.append([
            "Security Guard Service",
            "-",
            "0",
            str(total_days),
            money(shift_rate),
            money(0),
        ])

    bill_rows.append([
        "",
        "",
        "",
        "",
        "Gross Amount",
        money(data.get("gross_amount", 0)),
    ])

    bill_table = Table(
        bill_rows,
        colWidths=[
            48 * mm,
            20 * mm,
            20 * mm,
            20 * mm,
            30 * mm,
            32 * mm,
        ]
    )

    bill_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
            ("FONTNAME", (4, -1), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )

    story.append(bill_table)

    story.append(Spacer(1, 12))

    # --------------------------------------------------------
    # GST / TOTAL
    # --------------------------------------------------------

    totals = [
        [
            "Gross Amount",
            money(data.get("gross_amount", 0))
        ],
        [
            "CGST",
            money(data.get("cgst_amount", 0))
        ],
        [
            "SGST",
            money(data.get("sgst_amount", 0))
        ],
        [
            "GRAND TOTAL",
            money(data.get("total_amount", 0))
        ],
    ]

    totals_table = Table(
        totals,
        colWidths=[
            125 * mm,
            45 * mm,
        ]
    )

    totals_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold"),
            ("BACKGROUND", (0, 3), (-1, 3), colors.lightgrey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )

    story.append(totals_table)

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            "<b>Amount in Words:</b> "
            + amount_in_words(
                data.get("total_amount", 0)
            ),
            styles["normal"]
        )
    )

    story.append(Spacer(1, 30))

    signature = Table(
        [
            [
                "Prepared By",
                "Authorized Signature",
            ]
        ],
        colWidths=[
            85 * mm,
            85 * mm,
        ]
    )

    signature.setStyle(
        TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("LINEABOVE", (0, 0), (-1, 0), 0.5, colors.black),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
        ])
    )

    story.append(signature)

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()