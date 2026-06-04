"""
Results endpoints: devuelve los resultados (PNG, criterios, summary) de un analisis.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from sembraria.api.auth import get_current_user
from sembraria.database import get_db
from sembraria.models.analysis import Analysis
from sembraria.models.result import Result
from sembraria.models.user import User
from sembraria.schemas.result import ResultOut
from pathlib import Path

router = APIRouter()


@router.get("/{analysis_id}", response_model=ResultOut)
async def get_result(
    analysis_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene el resultado de un analisis por analysis_id."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analisis no encontrado")
    if analysis.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    result = db.query(Result).filter(Result.analysis_id == analysis_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Resultado no encontrado")

    return result


@router.get("/{analysis_id}/png")
async def get_png(
    analysis_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sirve el PNG generado para un analisis."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analisis no encontrado")
    if analysis.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    result = db.query(Result).filter(Result.analysis_id == analysis_id).first()
    if not result or not result.png_path:
        raise HTTPException(status_code=404, detail="PNG no disponible")

    png_path = Path(result.png_path)
    if not png_path.exists():
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {png_path}")

    return FileResponse(png_path, media_type="image/png", filename=png_path.name)
