import uuid

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_db
from app.middleware.auth import require_director
from app.models.usuario import Usuario
from app.schemas.log_auditoria import LogAuditoriaResponse, LogAuditoriaListResponse
from app.services.auditoria_service import list_logs, get_logs_by_usuario

router = APIRouter(prefix="/api/v1/auditoria", tags=["auditoria"])


@router.get("", response_model=LogAuditoriaListResponse)
def list_logs_endpoint(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    usuario_id: str | None = Query(None),
    entidad_tipo: str | None = Query(None),
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    uid = uuid.UUID(usuario_id) if usuario_id else None
    logs, total = list_logs(db, page=page, limit=limit, usuario_id=uid, entidad_tipo=entidad_tipo)
    return LogAuditoriaListResponse(
        items=[LogAuditoriaResponse.model_validate(l) for l in logs],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/usuario/{usuario_id}", response_model=LogAuditoriaListResponse)
def get_logs_by_usuario_endpoint(
    usuario_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    logs, total = get_logs_by_usuario(db, uuid.UUID(usuario_id), page=page, limit=limit)
    return LogAuditoriaListResponse(
        items=[LogAuditoriaResponse.model_validate(l) for l in logs],
        total=total,
        page=page,
        limit=limit,
    )
