import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.database import get_db
from app.middleware.auth import get_current_user, require_director
from app.models.usuario import Usuario
from app.schemas.boletin import (
    BoletinCreate,
    BoletinUpdate,
    BoletinResponse,
    BoletinListResponse,
    SeccionResponse,
    CompletarSeccionRequest,
    NotaAsignarRequest,
    NotaDesasignarRequest,
    NotaBoletinResponse,
    NotaBoletinListResponse,
)
from app.schemas.seccion import SeccionUpdate
from app.services.boletin_service import (
    create_boletin,
    list_boletines,
    get_boletin_with_secciones,
    update_boletin,
    delete_boletin,
    completar_seccion,
    cerrar_boletin,
    get_seccion_by_tipo,
    list_secciones,
    update_seccion,
    get_notas_disponibles,
    get_notas_asignadas,
    asignar_notas,
    desasignar_notas,
)

router = APIRouter(prefix="/api/v1/boletines", tags=["boletines"])


def _calcular_progreso(secciones: list) -> int:
    """Calcula progreso como % de secciones con contenido real o completadas."""
    if not secciones:
        return 0
    avanzadas = 0
    for s in secciones:
        if s.estado == "completada":
            avanzadas += 1
        elif s.contenido and s.contenido != {}:
            # Para notas_colaboradores, solo contar si tiene notas reales
            if s.tipo == "notas_colaboradores":
                if s.contenido.get("total_notas", 0) > 0:
                    avanzadas += 1
            else:
                avanzadas += 1
    return round((avanzadas / len(secciones)) * 100)


@router.get("", response_model=BoletinListResponse)
def list_boletines_endpoint(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    estado: str | None = Query(None),
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = user.id if user.rol != "director" else None
    boletines, total = list_boletines(db, page=page, limit=limit, estado=estado, user_id=user_id)
    items = []
    for b in boletines:
        _, secciones = get_boletin_with_secciones(db, b.id)
        items.append(BoletinResponse(
            id=b.id,
            nombre=b.nombre,
            periodo_inicio=b.periodo_inicio,
            periodo_fin=b.periodo_fin,
            fecha_publicacion_estimada=b.fecha_publicacion_estimada,
            estado=b.estado,
            creado_por=b.creado_por,
            fecha_creacion=b.fecha_creacion,
            fecha_cierre=b.fecha_cierre,
            secciones=[SeccionResponse.model_validate(s) for s in secciones],
            progreso=_calcular_progreso(secciones),
        ))
    return BoletinListResponse(items=items, total=total, page=page, limit=limit)


@router.post("", response_model=BoletinResponse, status_code=status.HTTP_201_CREATED)
def create_boletin_endpoint(
    body: BoletinCreate,
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    boletin = create_boletin(db, body, user.id)
    _, secciones = get_boletin_with_secciones(db, boletin.id)
    return BoletinResponse(
        id=boletin.id,
        nombre=boletin.nombre,
        periodo_inicio=boletin.periodo_inicio,
        periodo_fin=boletin.periodo_fin,
        fecha_publicacion_estimada=boletin.fecha_publicacion_estimada,
        estado=boletin.estado,
        creado_por=boletin.creado_por,
        fecha_creacion=boletin.fecha_creacion,
        fecha_cierre=boletin.fecha_cierre,
        secciones=[SeccionResponse.model_validate(s) for s in secciones],
        progreso=_calcular_progreso(secciones),
    )


@router.get("/{boletin_id}", response_model=BoletinResponse)
def get_boletin_endpoint(
    boletin_id: str,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    boletin, secciones = get_boletin_with_secciones(db, uuid.UUID(boletin_id))
    return BoletinResponse(
        id=boletin.id,
        nombre=boletin.nombre,
        periodo_inicio=boletin.periodo_inicio,
        periodo_fin=boletin.periodo_fin,
        fecha_publicacion_estimada=boletin.fecha_publicacion_estimada,
        estado=boletin.estado,
        creado_por=boletin.creado_por,
        fecha_creacion=boletin.fecha_creacion,
        fecha_cierre=boletin.fecha_cierre,
        secciones=[SeccionResponse.model_validate(s) for s in secciones],
        progreso=_calcular_progreso(secciones),
    )


@router.put("/{boletin_id}", response_model=BoletinResponse)
def update_boletin_endpoint(
    boletin_id: str,
    body: BoletinUpdate,
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    boletin = update_boletin(db, uuid.UUID(boletin_id), body)
    _, secciones = get_boletin_with_secciones(db, boletin.id)
    return BoletinResponse(
        id=boletin.id,
        nombre=boletin.nombre,
        periodo_inicio=boletin.periodo_inicio,
        periodo_fin=boletin.periodo_fin,
        fecha_publicacion_estimada=boletin.fecha_publicacion_estimada,
        estado=boletin.estado,
        creado_por=boletin.creado_por,
        fecha_creacion=boletin.fecha_creacion,
        fecha_cierre=boletin.fecha_cierre,
        secciones=[SeccionResponse.model_validate(s) for s in secciones],
        progreso=_calcular_progreso(secciones),
    )


@router.delete("/{boletin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_boletin_endpoint(
    boletin_id: str,
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    delete_boletin(db, uuid.UUID(boletin_id))


@router.post("/{boletin_id}/completar-seccion", response_model=SeccionResponse)
def completar_seccion_endpoint(
    boletin_id: str,
    body: CompletarSeccionRequest,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    seccion = completar_seccion(db, uuid.UUID(boletin_id), body.tipo, user.id)
    return SeccionResponse.model_validate(seccion)


@router.post("/{boletin_id}/cerrar", response_model=BoletinResponse)
def cerrar_boletin_endpoint(
    boletin_id: str,
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    boletin = cerrar_boletin(db, uuid.UUID(boletin_id))
    _, secciones = get_boletin_with_secciones(db, boletin.id)
    return BoletinResponse(
        id=boletin.id,
        nombre=boletin.nombre,
        periodo_inicio=boletin.periodo_inicio,
        periodo_fin=boletin.periodo_fin,
        fecha_publicacion_estimada=boletin.fecha_publicacion_estimada,
        estado=boletin.estado,
        creado_por=boletin.creado_por,
        fecha_creacion=boletin.fecha_creacion,
        fecha_cierre=boletin.fecha_cierre,
        secciones=[SeccionResponse.model_validate(s) for s in secciones],
        progreso=_calcular_progreso(secciones),
    )


@router.get("/{boletin_id}/secciones", response_model=list[SeccionResponse])
def list_secciones_endpoint(
    boletin_id: str,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    secciones = list_secciones(db, uuid.UUID(boletin_id))
    return [SeccionResponse.model_validate(s) for s in secciones]


@router.get("/{boletin_id}/secciones/{tipo}", response_model=SeccionResponse)
def get_seccion_endpoint(
    boletin_id: str,
    tipo: str,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    seccion = get_seccion_by_tipo(db, uuid.UUID(boletin_id), tipo)
    return SeccionResponse.model_validate(seccion)


@router.put("/{boletin_id}/secciones/{tipo}", response_model=SeccionResponse)
def update_seccion_endpoint(
    boletin_id: str,
    tipo: str,
    body: SeccionUpdate,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    seccion = update_seccion(db, uuid.UUID(boletin_id), tipo, body.contenido)
    return SeccionResponse.model_validate(seccion)


# ── Notas: asignación a boletín ──────────────────────────────────────────────


@router.get("/{boletin_id}/notas/disponibles", response_model=NotaBoletinListResponse)
def notas_disponibles_endpoint(
    boletin_id: str,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Notas que no están asignadas a ningún boletín."""
    notas = get_notas_disponibles(db, uuid.UUID(boletin_id))
    return NotaBoletinListResponse(
        items=[NotaBoletinResponse.model_validate(n) for n in notas],
        total=len(notas),
    )


@router.get("/{boletin_id}/notas/asignadas", response_model=NotaBoletinListResponse)
def notas_asignadas_endpoint(
    boletin_id: str,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Notas asignadas a este boletín."""
    notas = get_notas_asignadas(db, uuid.UUID(boletin_id))
    return NotaBoletinListResponse(
        items=[NotaBoletinResponse.model_validate(n) for n in notas],
        total=len(notas),
    )


@router.post("/{boletin_id}/notas/asignar")
def asignar_notas_endpoint(
    boletin_id: str,
    body: NotaAsignarRequest,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Asigna notas seleccionadas al boletín."""
    count = asignar_notas(db, uuid.UUID(boletin_id), body.nota_ids)
    # Retornar progreso actualizado
    _, secciones = get_boletin_with_secciones(db, uuid.UUID(boletin_id))
    return {"asignadas": count, "progreso": _calcular_progreso(secciones)}


@router.post("/{boletin_id}/notas/desasignar")
def desasignar_notas_endpoint(
    boletin_id: str,
    body: NotaDesasignarRequest,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Desasigna notas del boletín (las libera para reutilizar)."""
    count = desasignar_notas(db, uuid.UUID(boletin_id), body.nota_ids)
    # Retornar progreso actualizado
    _, secciones = get_boletin_with_secciones(db, uuid.UUID(boletin_id))
    return {"desasignadas": count, "progreso": _calcular_progreso(secciones)}
