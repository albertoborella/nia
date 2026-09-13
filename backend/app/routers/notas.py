import uuid

from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlmodel import Session
from typing import Annotated

from app.database import get_db
from app.middleware.auth import get_current_user, require_director
from app.models.usuario import Usuario
from app.schemas.nota import (
    NotaUpdate,
    NotaEstadoUpdate,
    NotaResponse,
    NotaListResponse,
)
from app.services.nota_service import (
    create_nota,
    list_notas,
    get_nota_by_id,
    update_nota,
    delete_nota,
    update_nota_estado,
    get_nota_file_path,
)

router = APIRouter(prefix="/api/v1/notas", tags=["notas"])


@router.get("", response_model=NotaListResponse)
def list_notas_endpoint(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    estado: str | None = Query(None),
    tema: str | None = Query(None),
    autor: str | None = Query(None),
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notas, total = list_notas(db, page=page, limit=limit, estado=estado, tema=tema, autor=autor)
    items = [NotaResponse.model_validate(n) for n in notas]
    return NotaListResponse(items=items, total=total, page=page, limit=limit)


@router.post("", response_model=NotaResponse, status_code=status.HTTP_201_CREATED)
async def create_nota_endpoint(
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    titulo: Annotated[str, Form()] = ...,
    autor: Annotated[str, Form()] = ...,
    archivo: Annotated[UploadFile, File()] = ...,
    fuente: Annotated[str | None, Form()] = None,
    tema: Annotated[str | None, Form()] = None,
):
    nota = create_nota(db, titulo, autor, archivo, user.id, fuente, tema)
    return NotaResponse.model_validate(nota)


@router.get("/{nota_id}", response_model=NotaResponse)
def get_nota_endpoint(
    nota_id: str,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    nota = get_nota_by_id(db, uuid.UUID(nota_id))
    return NotaResponse.model_validate(nota)


@router.put("/{nota_id}", response_model=NotaResponse)
def update_nota_endpoint(
    nota_id: str,
    body: NotaUpdate,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    nota = update_nota(db, uuid.UUID(nota_id), body)
    return NotaResponse.model_validate(nota)


@router.delete("/{nota_id}")
def delete_nota_endpoint(
    nota_id: str,
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    delete_nota(db, uuid.UUID(nota_id))
    return {"message": "Note deleted"}


@router.put("/{nota_id}/estado", response_model=NotaResponse)
def update_nota_estado_endpoint(
    nota_id: str,
    body: NotaEstadoUpdate,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    nota = update_nota_estado(db, uuid.UUID(nota_id), body, user.id)
    return NotaResponse.model_validate(nota)


@router.get("/{nota_id}/descarga")
def download_nota_endpoint(
    nota_id: str,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file_path, media_type = get_nota_file_path(db, uuid.UUID(nota_id))
    return FileResponse(path=str(file_path), media_type=media_type, filename=file_path.name)
