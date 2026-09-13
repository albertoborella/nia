import uuid
from datetime import datetime, timezone

from sqlmodel import Session, select, func

from app.models.boletin import Boletin
from app.models.nota import Nota
from app.models.seccion import Seccion
from app.schemas.boletin import BoletinCreate, BoletinUpdate
from app.utils.errors import NotFoundError, ConflictError, ValidationError

SECCIONES_DEFAULT = [
    {"tipo": "editorial", "orden": 1},
    {"tipo": "incidentes", "orden": 2},
    {"tipo": "notas_colaboradores", "orden": 3},
    {"tipo": "tabla_incidentes", "orden": 4},
    {"tipo": "auspiciantes", "orden": 5},
    {"tipo": "indice", "orden": 6},
]


def create_boletin(db: Session, data: BoletinCreate, user_id: uuid.UUID) -> Boletin:
    boletin = Boletin(
        nombre=data.nombre,
        periodo_inicio=data.periodo_inicio,
        periodo_fin=data.periodo_fin,
        fecha_publicacion_estimada=data.fecha_publicacion_estimada,
        estado="borrador",
        creado_por=user_id,
    )
    db.add(boletin)
    db.flush()

    for sec in SECCIONES_DEFAULT:
        seccion = Seccion(
            boletin_id=boletin.id,
            tipo=sec["tipo"],
            orden=sec["orden"],
            estado="pendiente",
            contenido={},
        )
        db.add(seccion)

    db.commit()
    db.refresh(boletin)
    return boletin


def list_boletines(
    db: Session, page: int = 1, limit: int = 20, estado: str | None = None, user_id: uuid.UUID | None = None
) -> tuple[list[Boletin], int]:
    query = select(Boletin)
    count_query = select(func.count()).select_from(Boletin)

    if estado:
        query = query.where(Boletin.estado == estado)
        count_query = count_query.where(Boletin.estado == estado)

    if user_id:
        query = query.where(Boletin.creado_por == user_id)
        count_query = count_query.where(Boletin.creado_por == user_id)

    total = db.exec(count_query).one()
    offset = (page - 1) * limit
    boletines = db.exec(query.order_by(Boletin.fecha_creacion.desc()).offset(offset).limit(limit)).all()

    return list(boletines), total


def get_boletin_by_id(db: Session, boletin_id: uuid.UUID) -> Boletin:
    boletin = db.query(Boletin).filter(Boletin.id == boletin_id).first()
    if not boletin:
        raise NotFoundError("Boletin", str(boletin_id))
    return boletin


def get_boletin_with_secciones(db: Session, boletin_id: uuid.UUID) -> tuple[Boletin, list[Seccion]]:
    boletin = get_boletin_by_id(db, boletin_id)
    secciones = db.exec(
        select(Seccion).where(Seccion.boletin_id == boletin_id).order_by(Seccion.orden)
    ).all()
    return boletin, list(secciones)


def update_boletin(db: Session, boletin_id: uuid.UUID, data: BoletinUpdate) -> Boletin:
    boletin = get_boletin_by_id(db, boletin_id)
    if boletin.estado != "borrador":
        raise ConflictError("Can only update boletin in 'borrador' state")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(boletin, key, value)

    db.add(boletin)
    db.commit()
    db.refresh(boletin)
    return boletin


def completar_seccion(db: Session, boletin_id: uuid.UUID, tipo: str, user_id: uuid.UUID) -> Seccion:
    boletin = get_boletin_by_id(db, boletin_id)
    if boletin.estado == "cerrado":
        raise ConflictError("Cannot complete sections on a closed boletin")

    seccion = db.query(Seccion).filter(
        Seccion.boletin_id == boletin_id,
        Seccion.tipo == tipo,
    ).first()
    if not seccion:
        raise NotFoundError("Seccion", tipo)

    seccion.estado = "completada"
    seccion.completado_por = user_id
    seccion.fecha_completado = datetime.now(timezone.utc)

    db.add(seccion)
    db.commit()
    db.refresh(seccion)
    return seccion


def cerrar_boletin(db: Session, boletin_id: uuid.UUID) -> Boletin:
    boletin = get_boletin_by_id(db, boletin_id)

    secciones = db.exec(
        select(Seccion).where(Seccion.boletin_id == boletin_id)
    ).all()

    incompletas = [s for s in secciones if s.estado != "completada"]
    if incompletas:
        tipos = [s.tipo for s in incompletas]
        raise ConflictError(f"Boletin has incomplete sections: {', '.join(tipos)}")

    boletin.estado = "cerrado"
    boletin.fecha_cierre = datetime.now(timezone.utc)
    db.add(boletin)
    db.commit()
    db.refresh(boletin)
    return boletin


def get_seccion_by_tipo(db: Session, boletin_id: uuid.UUID, tipo: str) -> Seccion:
    seccion = db.query(Seccion).filter(
        Seccion.boletin_id == boletin_id,
        Seccion.tipo == tipo,
    ).first()
    if not seccion:
        raise NotFoundError("Seccion", tipo)
    return seccion


def list_secciones(db: Session, boletin_id: uuid.UUID) -> list[Seccion]:
    secciones = db.exec(
        select(Seccion).where(Seccion.boletin_id == boletin_id).order_by(Seccion.orden)
    ).all()
    return list(secciones)


def update_seccion(db: Session, boletin_id: uuid.UUID, tipo: str, contenido: dict) -> Seccion:
    seccion = get_seccion_by_tipo(db, boletin_id, tipo)
    seccion.contenido = contenido
    db.add(seccion)
    db.commit()
    db.refresh(seccion)
    return seccion


def delete_boletin(db: Session, boletin_id: uuid.UUID) -> None:
    boletin = get_boletin_by_id(db, boletin_id)
    secciones = db.exec(select(Seccion).where(Seccion.boletin_id == boletin_id)).all()
    for seccion in secciones:
        db.delete(seccion)
    db.flush()

    # Desasignar notas antes de borrar el boletin
    notas = db.exec(select(Nota).where(Nota.boletin_asignado == boletin_id)).all()
    for nota in notas:
        nota.boletin_asignado = None
        db.add(nota)
    db.flush()

    db.delete(boletin)
    db.commit()


def get_notas_disponibles(db: Session, boletin_id: uuid.UUID) -> list[Nota]:
    """Notas que NO estan asignadas a ningun boletin."""
    notas = db.exec(
        select(Nota).where(Nota.boletin_asignado.is_(None)).order_by(Nota.fecha_recepcion.desc())
    ).all()
    return list(notas)


def get_notas_asignadas(db: Session, boletin_id: uuid.UUID) -> list[Nota]:
    """Notas asignadas a este boletin especifico."""
    notas = db.exec(
        select(Nota).where(Nota.boletin_asignado == boletin_id).order_by(Nota.fecha_recepcion.desc())
    ).all()
    return list(notas)


def asignar_notas(db: Session, boletin_id: uuid.UUID, nota_ids: list[uuid.UUID]) -> int:
    """Asigna notas al boletin. Retorna cantidad asignada."""
    boletin = get_boletin_by_id(db, boletin_id)  # valida que exista

    if not nota_ids:
        raise ValidationError(code="EMPTY_LIST", message="No note IDs provided")

    notas = db.exec(select(Nota).where(Nota.id.in_(nota_ids))).all()
    if len(notas) != len(nota_ids):
        found_ids = {n.id for n in notas}
        missing = [str(nid) for nid in nota_ids if nid not in found_ids]
        raise NotFoundError("Nota", ", ".join(missing))

    count = 0
    for nota in notas:
        if nota.boletin_asignado is not None and nota.boletin_asignado != boletin_id:
            # Nota ya pertenece a otro boletin — permitir reasignar
            pass
        nota.boletin_asignado = boletin_id
        db.add(nota)
        count += 1

    # Actualizar contenido de la seccion notas_colaboradores
    _sync_seccion_notas(db, boletin_id)

    db.commit()
    return count


def desasignar_notas(db: Session, boletin_id: uuid.UUID, nota_ids: list[uuid.UUID]) -> int:
    """Desasigna notas del boletin (las libera). Retorna cantidad desasignada."""
    if not nota_ids:
        raise ValidationError(code="EMPTY_LIST", message="No note IDs provided")

    notas = db.exec(
        select(Nota).where(
            Nota.id.in_(nota_ids),
            Nota.boletin_asignado == boletin_id,
        )
    ).all()

    count = 0
    for nota in notas:
        nota.boletin_asignado = None
        db.add(nota)
        count += 1

    # Actualizar contenido de la seccion notas_colaboradores
    _sync_seccion_notas(db, boletin_id)

    db.commit()
    return count


def _sync_seccion_notas(db: Session, boletin_id: uuid.UUID) -> None:
    """Sincroniza el contenido de la seccion notas_colaboradores con las notas asignadas."""
    notas_asignadas = db.exec(
        select(Nota).where(Nota.boletin_asignado == boletin_id)
    ).all()

    seccion = db.query(Seccion).filter(
        Seccion.boletin_id == boletin_id,
        Seccion.tipo == "notas_colaboradores",
    ).first()

    if seccion:
        seccion.contenido = {
            "notas_ids": [str(n.id) for n in notas_asignadas],
            "total_notas": len(notas_asignadas),
        }
        db.add(seccion)
