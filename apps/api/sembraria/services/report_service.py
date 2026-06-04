"""
Report Service: genera PDF con ReportLab.
Incluye el PNG generado por zonal_extraction embebido en el PDF.
"""
import logging
from datetime import datetime
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from sembraria.config import get_crops_config
from sembraria.models.analysis import Analysis
from sembraria.models.farm import Farm
from sembraria.models.user import User

logger = logging.getLogger(__name__)


def generate_pdf_report(farm: Farm, analysis: Analysis, user: User) -> BytesIO:
    """
    Genera un PDF profesional con el reporte del analisis.
    Embebe el PNG generado por zonal_extraction si esta disponible.
    Devuelve un BytesIO listo para StreamingResponse.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        title=f"SembrarIA - {farm.name}",
        author="SembrarIA - Universidad de la Amazonia",
        subject="Reporte de aptitud agricola con datos satelitales",
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#1B5E20"),
        spaceAfter=20,
    )
    h2_style = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=colors.HexColor("#00C853"),
        spaceAfter=12,
    )

    elements = []

    elements.append(Paragraph("SembrarIA &mdash; Reporte de Aptitud Agr&iacute;cola", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    crops = get_crops_config().get("crops", [])
    crop = next((c for c in crops if c["id"] == analysis.cultivo), {})
    crop_label = crop.get("label", analysis.cultivo.capitalize())

    info_data = [
        ["Finca:", farm.name],
        ["Municipio:", farm.municipio],
        ["Cultivo evaluado:", crop_label],
        ["Productor:", user.full_name],
        ["Email:", user.email],
        ["Fecha del an&aacute;lisis:", analysis.created_at.strftime("%Y-%m-%d %H:%M UTC")],
        ["Estado:", analysis.status.value.upper()],
    ]
    info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
    info_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0FFF4")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1B5E20")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
            ]
        )
    )
    elements.append(info_table)
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Resultados", h2_style))

    if analysis.hectares_aptas is not None and analysis.hectares_totales is not None:
        resultados = [
            ["H&eacute;ctareas aptas:", f"{float(analysis.hectares_aptas):.2f} ha"],
            [
                "H&eacute;ctareas totales:",
                f"{float(analysis.hectares_totales):.2f} ha",
            ],
            [
                "Porcentaje apto:",
                f"{float(analysis.porcentaje_apto):.1f}%",
            ],
        ]
        result_table = Table(resultados, colWidths=[2 * inch, 4 * inch])
        result_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("TEXTCOLOR", (1, 0), (1, 0), colors.HexColor("#00C853")),
                    ("FONTSIZE", (1, 0), (1, 0), 18),
                    ("FONTSIZE", (0, 0), (-1, -1), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        elements.append(result_table)
        elements.append(Spacer(1, 0.3 * inch))

    # === Embed PNG (FIX bug PDF sin imagen) ===
    # Si el analisis tiene un PNG generado, lo embebemos en el PDF.
    from sembraria.database import SessionLocal
    from sembraria.models.result import Result

    db = SessionLocal()
    try:
        result = db.query(Result).filter(Result.analysis_id == analysis.id).first()
        if result and result.png_path:
            png_path = Path(result.png_path)
            if png_path.exists():
                elements.append(Paragraph("Mapa de Aptitud", h2_style))
                try:
                    img = Image(str(png_path), width=5 * inch, height=5 * inch)
                    elements.append(img)
                    elements.append(Spacer(1, 0.2 * inch))
                except Exception as e:
                    logger.warning(f"No se pudo embeber el PNG en el PDF: {e}")
    finally:
        db.close()

    # === Criterios ===
    if analysis.criterios:
        elements.append(Paragraph("Criterios de aptitud", h2_style))
        criteria_data = [["Criterio", "Estado", "Detalle"]]
        for c in analysis.criterios:
            status_icon = "OK" if c.get("status") == "pass" else "!"
            criteria_data.append(
                [
                    c.get("name", ""),
                    status_icon,
                    c.get("detail", ""),
                ]
            )
        criteria_table = Table(criteria_data, colWidths=[1.8 * inch, 0.5 * inch, 3.7 * inch])
        criteria_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B5E20")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
                ]
            )
        )
        elements.append(criteria_table)
        elements.append(Spacer(1, 0.3 * inch))

    elements.append(Spacer(1, 0.5 * inch))
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#999999"),
    )
    elements.append(
        Paragraph(
            "&copy; 2026 SembrarIA &middot; Universidad de la Amazon&iacute;a &middot; "
            "CopernicusLAC Hackathon. Datos satelitales: Sentinel-2, Sentinel-1, "
            "ERA5, MODIS, SRTM. <i>Este reporte se gener&oacute; a partir de "
            "datos sint&eacute;ticos de demostraci&oacute;n con fines ilustrativos.</i>",
            footer_style,
        )
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer
