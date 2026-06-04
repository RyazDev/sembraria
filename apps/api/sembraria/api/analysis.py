"""
Analysis endpoints: analisis sincrono de aptitud por cultivo.
Hace extraccion zonal (rasterio.mask) del raster de aptitud sobre el poligono de la finca.

Trazabilidad: cada resultado registra model_version, model_algorithm,
raster_inputs y config_snapshot para reproducibilidad.
"""
import logging
import time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from sembraria import __version__
from sembraria.api.auth import get_current_user
from sembraria.config import get_crops_config, get_raster_config, get_settings
from sembraria.database import get_db
from sembraria.models.analysis import Analysis, AnalysisStatus
from sembraria.models.farm import Farm
from sembraria.models.result import Result
from sembraria.models.user import User
from sembraria.schemas.analysis import AnalysisOut, AnalysisRequest
from sembraria.services.audit_service import log_event
from sembraria.services.zonal_extraction import MODEL_ALGORITHM, MODEL_VERSION, run_zonal_extraction

router = APIRouter()
logger = logging.getLogger(__name__)


def _analysis_to_out(analysis: Analysis) -> AnalysisOut:
    return AnalysisOut.model_validate(analysis)


@router.get("", response_model=list[AnalysisOut])
async def list_analyses(
    farm_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista los analisis del usuario actual (opcionalmente filtrados por farm)."""
    q = db.query(Analysis).filter(Analysis.user_id == current_user.id)
    if farm_id:
        q = q.filter(Analysis.farm_id == farm_id)
    return [_analysis_to_out(a) for a in q.order_by(Analysis.created_at.desc()).all()]


@router.get("/{analysis_id}", response_model=AnalysisOut)
async def get_analysis(
    analysis_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene un analisis por ID."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analisis no encontrado")
    if analysis.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    return _analysis_to_out(analysis)


@router.post("/farms/{farm_id}/analyze", response_model=AnalysisOut)
async def analyze_farm(
    farm_id: uuid.UUID,
    payload: AnalysisRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analisis SINCRONO de aptitud para una finca.
    - Valida el cultivo
    - Recorta el raster de aptitud al poligono de la finca
    - Cuenta pixeles aptos vs no aptos
    - Genera PNG del recorte
    - Persiste resultado en DB
    - Registra inicio y fin en audit log
    Duracion tipica: 0.5-5 segundos (raster sintetico demo).
    """
    start_ms = int(time.time() * 1000)

    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    if farm.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    crops = get_crops_config().get("crops", [])
    cultivo_ids = [c["id"] for c in crops]
    if payload.cultivo not in cultivo_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Cultivo '{payload.cultivo}' no soportado. Disponibles: {cultivo_ids}",
        )

    analysis = Analysis(
        farm_id=farm.id,
        user_id=current_user.id,
        cultivo=payload.cultivo,
        status=AnalysisStatus.PROCESSING,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    log_event(
        db,
        user_id=str(current_user.id),
        action="analyze_started",
        resource="analysis",
        resource_id=str(analysis.id),
        request=request,
        details={"farm_id": str(farm.id), "cultivo": payload.cultivo},
    )

    try:
        result_data = run_zonal_extraction(
            farm=farm,
            cultivo=payload.cultivo,
            analysis_id=analysis.id,
        )

        analysis.status = AnalysisStatus.COMPLETED
        analysis.hectares_aptas = result_data["hectares_aptas"]
        analysis.hectares_totales = result_data["hectares_totales"]
        analysis.porcentaje_apto = result_data["porcentaje_apto"]
        analysis.criterios = result_data["criteria"]
        analysis.execution_time_ms = int(time.time() * 1000) - start_ms
        analysis.completed_at = datetime.now(timezone.utc)

        result = Result(
            analysis_id=analysis.id,
            png_path=result_data["png_path"],
            png_url=result_data["png_url"],
            pdf_path=result_data.get("pdf_path"),
            summary=result_data["summary"],
            criteria=result_data["criteria"],
            slope_breakdown=result_data.get("slope_breakdown"),
            model_version=MODEL_VERSION,
            model_algorithm=MODEL_ALGORITHM,
            raster_inputs=[
                {
                    "name": f"aptitud_{payload.cultivo.upper()}.tif",
                    "purpose": "suitability_mask",
                    "synthetic": True,
                }
            ],
            config_snapshot={
                "raster_config": get_raster_config().get("raster", {}),
                "app_version": __version__,
                "app_env": get_settings().app_env,
            },
        )
        db.add(result)
        db.commit()
        db.refresh(analysis)

        log_event(
            db,
            user_id=str(current_user.id),
            action="analyze_completed",
            resource="analysis",
            resource_id=str(analysis.id),
            request=request,
            details={
                "farm_id": str(farm.id),
                "cultivo": payload.cultivo,
                "hectares_aptas": float(analysis.hectares_aptas or 0),
                "porcentaje_apto": float(analysis.porcentaje_apto or 0),
                "execution_time_ms": analysis.execution_time_ms,
            },
        )

        return _analysis_to_out(analysis)

    except Exception as e:
        logger.error(f"Error en analisis: {e}", exc_info=True)
        analysis.status = AnalysisStatus.FAILED
        analysis.error_message = str(e)
        analysis.execution_time_ms = int(time.time() * 1000) - start_ms
        db.commit()

        log_event(
            db,
            user_id=str(current_user.id),
            action="analyze_failed",
            resource="analysis",
            resource_id=str(analysis.id),
            request=request,
            details={"farm_id": str(farm.id), "cultivo": payload.cultivo, "error": str(e)},
        )

        raise HTTPException(
            status_code=500,
            detail=f"Error procesando analisis: {str(e)}",
        )
