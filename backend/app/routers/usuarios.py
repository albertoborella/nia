from fastapi import APIRouter, Depends, Query, Response, status
from sqlmodel import Session

from app.database import get_db
from app.middleware.auth import require_director
from app.models.usuario import Usuario
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    UsuarioListResponse,
)
from app.services.usuario_service import (
    get_user_by_id,
    list_users,
    create_user,
    update_user,
    reset_user_password,
)
from app.schemas.auth import MessageResponse

router = APIRouter(prefix="/api/v1/usuarios", tags=["usuarios"])


@router.get("", response_model=UsuarioListResponse)
def list_usuarios(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    rol: str | None = Query(None),
    _user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    users, total = list_users(db, page=page, limit=limit, rol=rol)
    return UsuarioListResponse(
        items=[UsuarioResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        limit=limit,
    )


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def create_usuario(
    body: UsuarioCreate,
    _user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    user = create_user(db, body)
    return UsuarioResponse.model_validate(user)


@router.put("/{user_id}", response_model=UsuarioResponse)
def update_usuario(
    user_id: str,
    body: UsuarioUpdate,
    _user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    import uuid
    user = update_user(db, uuid.UUID(user_id), body)
    return UsuarioResponse.model_validate(user)


@router.post("/{user_id}/reset-password")
def reset_password(
    user_id: str,
    _user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    import uuid
    reset_user_password(db, uuid.UUID(user_id))
    return MessageResponse(message="Password reset email sent")
