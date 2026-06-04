"""
Reports endpoints: genera y descarga PDF con ReportLab.
"""
import uuid
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from sembraria.api.auth import get_current_user
from sembraria.database import get_db
from sembraria.models.analysis import Analysis
from sembraria.models.farm import Farm
from sembraria.models.user import User
from sembraria.services.report_service import generate_pdf_report

router = APIRouter()


@router.get("/{analysis_id}/download")
async def download_report(
    analysis_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Genera y descarga un PDF con el reporte del analisis."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analisis no encontrado")
    if analysis.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    farm = db.query(Farm).filter(Farm.id == analysis.farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Finca no encontrada")

    pdf_bytes: BytesIO = generate_pdf_report(
        farm=farm,
        analysis=analysis,
        user=current_user,
    )

    filename = f"sembraria_reporte_{farm.name.replace(' ', '_')}_{analysis.cultivo}.pdf"
    return StreamingResponse(
        pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
