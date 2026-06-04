"""
Prices endpoint: precios de mercado desde DB.

Trazabilidad:
  - Cada respuesta incluye `is_synthetic` y `data_provenance` para que el
    frontend pueda mostrar un banner honesto cuando los datos son mock.
  - En este MVP todos los precios son sinteticos (generados por el seed).
    Cuando se conecten scrapers de FEDECACAO/FNC, deberan insertarse
    con is_synthetic=false y source_url apuntando al sitio oficial.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import desc
from sqlalchemy.orm import Session

from sembraria.api.auth import get_current_user
from sembraria.database import get_db
from sembraria.models.market_price import MarketPrice
from sembraria.models.user import User

router = APIRouter()


class MarketPriceOut(BaseModel):
    """Precio de mercado de un producto agropecuario."""
    model_config = ConfigDict(from_attributes=True)

    producto: str
    precio_cop_kg: float
    unidad: str
    fuente: str
    cambio_porcentual: Optional[float] = None
    municipio: Optional[str] = None
    recorded_at: datetime
    is_synthetic: bool
    source_url: Optional[str] = None
    fetched_at: Optional[datetime] = None


@router.get("/market-prices", response_model=List[MarketPriceOut])
async def get_market_prices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Devuelve el ultimo precio registrado por cada producto.

    Trazabilidad: la respuesta se entrega con `is_synthetic` por registro.
    La UI debe mostrar un banner cuando todos los precios son sinteticos.
    """
    prices = (
        db.query(MarketPrice)
        .distinct(MarketPrice.producto)
        .order_by(MarketPrice.producto, MarketPrice.recorded_at.desc())
        .all()
    )
    return [MarketPriceOut.model_validate(p) for p in prices]


@router.get("/market-prices/provenance")
async def get_market_prices_provenance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Resumen de la procedencia de los datos de precios.

    Util para que el frontend muestre un banner honesto:
      { data_provenance: "synthetic" | "mixed" | "real",
        total: 30, synthetic: 30, real: 0,
        message: "..." }
    """
    total = db.query(MarketPrice).count()
    synthetic = db.query(MarketPrice).filter(MarketPrice.is_synthetic.is_(True)).count()
    real = total - synthetic
    if total == 0:
        provenance = "empty"
        message = "No hay precios registrados."
    elif real == 0:
        provenance = "synthetic"
        message = (
            "Los precios mostrados son DEMO (generados internamente). "
            "No usar para decisiones reales hasta conectar fuentes oficiales."
        )
    elif synthetic == 0:
        provenance = "real"
        message = "Precios en tiempo real desde fuentes oficiales."
    else:
        provenance = "mixed"
        message = (
            f"{real} precios reales y {synthetic} demo. "
            "Los registros demo no deben usarse para decisiones de mercado."
        )
    return {
        "data_provenance": provenance,
        "total": total,
        "synthetic": synthetic,
        "real": real,
        "message": message,
    }


@router.get("/market-prices/history/{producto}")
async def get_price_history(
    producto: str,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Devuelve el historial de precios de un producto en los ultimos N dias."""
    from datetime import timedelta

    since = datetime.utcnow() - timedelta(days=days)
    prices = (
        db.query(MarketPrice)
        .filter(MarketPrice.producto == producto, MarketPrice.recorded_at >= since)
        .order_by(MarketPrice.recorded_at.asc())
        .all()
    )
    return [
        {
            "precio_cop_kg": float(p.precio_cop_kg),
            "recorded_at": p.recorded_at.isoformat(),
            "is_synthetic": p.is_synthetic,
        }
        for p in prices
    ]
