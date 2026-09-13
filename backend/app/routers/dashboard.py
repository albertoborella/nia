from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.boletin import Boletin
from app.models.nota import Nota
from app.models.incidente import Incidente

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    # Boletines activos (borrador = en elaboración)
    boletines_activos = db.exec(
        select(func.count()).select_from(Boletin).where(Boletin.estado == "borrador")
    ).one()

    # Notas pendientes de revisión
    notas_pendientes = db.exec(
        select(func.count()).select_from(Nota).where(Nota.estado == "pendiente")
    ).one()

    # Incidentes del período (todos los que existen)
    incidentes_periodo = db.exec(
        select(func.count()).select_from(Incidente)
    ).one()

    return {
        "boletines_activos": boletines_activos,
        "notas_pendientes": notas_pendientes,
        "incidentes_periodo": incidentes_periodo,
        "tiempo_promedio": "—",
    }
