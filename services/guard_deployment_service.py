from pathlib import Path
from uuid import uuid4
from datetime import datetime

from sqlalchemy.orm import joinedload

from database.connection import SessionLocal
from database.models import Guard, Site
from database.guard_document import GuardDocument

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = PROJECT_ROOT / "uploads" / "guard_deployment_exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def generate_guard_deployment_pdf(guard_id, site_id):
    db = SessionLocal()
    try:
        guard = (
            db.query(Guard)
            .filter(Guard.id == guard_id)
            .first()
        )
        if not guard:
            raise ValueError("Guard not found.")

        site = (
            db.query(Site)
            .filter(Site.id == site_id)
            .first()
        )
        if not site:
            raise ValueError("Site not found.")

        documents = (
            db.query(GuardDocument)
            .filter(
                GuardDocument.guard_id == guard_id,
                GuardDocument.status == "Active",
            )
            .order_by(GuardDocument.document_type.asc())
            .all()
        )

        filename = (
            f"{guard.employee_id}_{site.site_code}_"
            f"guard_details_{uuid4().hex[:8]}.pdf"
        )
        output = EXPORT_DIR / filename

        styles = getSampleStyleSheet()
        title = ParagraphStyle(
            "TitleCustom",
            parent=styles["Title"],
            fontSize=18,
            leading=22,
            spaceAfter=12,
        )
        heading = ParagraphStyle(
            "HeadingCustom",
            parent=styles["Heading2"],
            fontSize=12,
            leading=15,
            spaceBefore=10,
            spaceAfter=6,
        )
        body = ParagraphStyle(
            "BodyCustom",
            parent=styles["BodyText"],
            fontSize=9.5,
            leading=13,
        )

        doc = SimpleDocTemplate(
            str(output),
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
        )

        story = [
            Paragraph("GUARD DEPLOYMENT DETAILS", title),
            Paragraph(
                f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
                body,
            ),
            Spacer(1, 8),
            Paragraph("Site Information", heading),
        ]

        site_rows = [
            ["Site Code", site.site_code or "-"],
            ["Site Name", site.name or "-"],
            ["Client", getattr(getattr(site, "client", None), "username", None) or "-"],
            ["Contact Person", site.contact_person or "-"],
            ["Contact Phone", site.contact_phone or "-"],
            [
                "Site Address",
                " ".join(
                    part for part in [
                        site.address,
                        site.city,
                        site.state,
                        site.pincode,
                    ] if part
                ) or "-",
            ],
        ]
        story.append(_table(site_rows))

        story.extend([
            Paragraph("Guard Information", heading),
        ])

        guard_rows = [
            ["Employee ID", guard.employee_id or "-"],
            ["Full Name", guard.name or "-"],
            ["Phone", guard.phone or "-"],
            ["Email", guard.email or "-"],
            ["Joining Date", str(guard.joining_date or "-")],
            ["Address", guard.address or "-"],
            ["Emergency Contact", guard.emergency_contact or "-"],
            ["Status", guard.status or "-"],
        ]
        story.append(_table(guard_rows))

        story.append(Paragraph("Documents Submitted", heading))
        if documents:
            doc_rows = [["Document", "File Name", "Status"]]
            for item in documents:
                doc_rows.append([
                    item.document_type,
                    item.original_filename or "-",
                    item.status or "Active",
                ])
            story.append(_table(doc_rows, header=True))
        else:
            story.append(Paragraph("No documents uploaded.", body))

        story.extend([
            Spacer(1, 15),
            Paragraph(
                "This document is generated from the Guard Management System. "
                "Original identification documents are supplied separately.",
                body,
            ),
        ])

        doc.build(story)
        return output
    finally:
        db.close()


def _table(rows, header=False):
    converted = []
    for row in rows:
        converted.append([Paragraph(str(cell), getSampleStyleSheet()["BodyText"]) for cell in row])

    table = Table(converted, colWidths=[48 * mm, 118 * mm] if not header else [65 * mm, 65 * mm, 36 * mm])
    style = [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        style.extend([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ])
    table.setStyle(TableStyle(style))
    return table
