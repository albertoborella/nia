import uuid

from sqlmodel import Session, select, func

from app.models.auspiciante import Auspiciante, BoletinAuspiciante
from app.schemas.auspiciante import AuspicianteCreate, AuspicianteUpdate
from app.utils.errors import NotFoundError


def create_auspiciante(db: Session, data: AuspicianteCreate) -> Auspiciante:
    auspiciante = Auspiciante(
        nombre=data.nombre,
        logo_url=data.logo_url,
        enlace=data.enlace,
        descripcion=data.descripcion,
    )
    db.add(auspiciante)
    db.commit()
    db.refresh(auspiciante)
    return auspiciante


def list_auspiciantes(
    db: Session, page: int = 1, limit: int = 20, activo: bool | None = None
) -> tuple[list[Auspiciante], int]:
    query = select(Auspiciante)
    count_query = select(func.count()).select_from(Auspiciante)

    if activo is not None:
        query = query.where(Auspiciante.activo == activo)
        count_query = count_query.where(Auspiciante.activo == activo)

    total = db.exec(count_query).one()
    offset = (page - 1) * limit
    auspiciantes = db.exec(query.order_by(Auspiciante.nombre).offset(offset).limit(limit)).all()

    return list(auspiciantes), total


def get_auspiciante_by_id(db: Session, auspiciante_id: uuid.UUID) -> Auspiciante:
    auspiciante = db.query(Auspiciante).filter(Auspiciante.id == auspiciante_id).first()
    if not auspiciante:
        raise NotFoundError("Auspiciante", str(auspiciante_id))
    return auspiciante


def update_auspiciante(db: Session, auspiciante_id: uuid.UUID, data: AuspicianteUpdate) -> Auspiciante:
    auspiciante = get_auspiciante_by_id(db, auspiciante_id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(auspiciante, key, value)
    db.add(auspiciante)
    db.commit()
    db.refresh(auspiciante)
    return auspiciante


def delete_auspiciante(db: Session, auspiciante_id: uuid.UUID) -> None:
    auspiciante = get_auspiciante_by_id(db, auspiciante_id)
    auspiciante.activo = False
    db.add(auspiciante)
    db.commit()


def get_auspiciantes_by_boletin(db: Session, boletin_id: uuid.UUID) -> list[Auspiciante]:
    stmt = (
        select(Auspiciante)
        .join(BoletinAuspiciante, BoletinAuspiciante.auspiciante_id == Auspiciante.id)
        .where(BoletinAuspiciante.boletin_id == boletin_id)
        .order_by(Auspiciante.nombre)
    )
    return list(db.exec(stmt).all())


def update_boletin_auspiciantes(
    db: Session, boletin_id: uuid.UUID, auspiciantes_ids: list[uuid.UUID]
) -> list[Auspiciante]:
    existing = db.exec(
        select(BoletinAuspiciante).where(BoletinAuspiciante.boletin_id == boletin_id)
    ).all()
    for rel in existing:
        db.delete(rel)

    for ausp_id in auspiciantes_ids:
        db.add(BoletinAuspiciante(boletin_id=boletin_id, auspiciante_id=ausp_id))

    db.commit()
    return get_auspiciantes_by_boletin(db, boletin_id)
