import uuid
from datetime import datetime, timezone

from sqlmodel import Session, select, func

from app.models.log_auditoria import LogAuditoria


def log_event(
    db: Session,
    usuario_id: uuid.UUID | None,
    accion: str,
    entidad_tipo: str,
    entidad_id: uuid.UUID | None = None,
    detalles: dict | None = None,
    ip: str | None = None,
) -> None:
    log = LogAuditoria(
        usuario_id=usuario_id,
        accion=accion,
        entidad_tipo=entidad_tipo,
        entidad_id=entidad_id,
        detalles=detalles or {},
        ip=ip,
    )
    db.add(log)
    db.commit()


def list_logs(
    db: Session,
    page: int = 1,
    limit: int = 20,
    usuario_id: uuid.UUID | None = None,
    entidad_tipo: str | None = None,
) -> tuple[list[LogAuditoria], int]:
    query = select(LogAuditoria)
    count_query = select(func.count()).select_from(LogAuditoria)

    if usuario_id:
        query = query.where(LogAuditoria.usuario_id == usuario_id)
        count_query = count_query.where(LogAuditoria.usuario_id == usuario_id)

    if entidad_tipo:
        query = query.where(LogAuditoria.entidad_tipo == entidad_tipo)
        count_query = count_query.where(LogAuditoria.entidad_tipo == entidad_tipo)

    total = db.exec(count_query).one()
    offset = (page - 1) * limit
    logs = db.exec(query.order_by(LogAuditoria.fecha.desc()).offset(offset).limit(limit)).all()

    return list(logs), total


def get_logs_by_usuario(
    db: Session, usuario_id: uuid.UUID, page: int = 1, limit: int = 20
) -> tuple[list[LogAuditoria], int]:
    return list_logs(db, page=page, limit=limit, usuario_id=usuario_id)
