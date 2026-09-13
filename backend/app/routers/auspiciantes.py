import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.database import get_db
from app.middleware.auth import get_current_user, require_director
from app.models.usuario import Usuario
from app.schemas.auspiciante import (
    AuspicianteCreate,
    AuspicianteUpdate,
    AuspicianteResponse,
    AuspicianteListResponse,
    BoletinAuspiciantesRequest,
)
from app.services.auspiciante_service import (
    create_auspiciante,
    list_auspiciantes,
    get_auspiciante_by_id,
    update_auspiciante,
    delete_auspiciante,
    get_auspiciantes_by_boletin,
    update_boletin_auspiciantes,
)

router = APIRouter(tags=["auspiciantes"])


@router.get("/api/v1/auspiciantes", response_model=AuspicianteListResponse)
def list_auspiciantes_endpoint(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    activo: bool | None = Query(None),
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    auspiciantes, total = list_auspiciantes(db, page=page, limit=limit, activo=activo)
    return AuspicianteListResponse(
        items=[AuspicianteResponse.model_validate(a) for a in auspiciantes],
        total=total,
        page=page,
        limit=limit,
    )


@router.post("/api/v1/auspiciantes", response_model=AuspicianteResponse, status_code=status.HTTP_201_CREATED)
def create_auspiciante_endpoint(
    body: AuspicianteCreate,
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    auspiciante = create_auspiciante(db, body)
    return AuspicianteResponse.model_validate(auspiciante)


@router.get("/api/v1/auspiciantes/{auspiciante_id}", response_model=AuspicianteResponse)
def get_auspiciante_endpoint(
    auspiciante_id: str,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    auspiciante = get_auspiciante_by_id(db, uuid.UUID(auspiciante_id))
    return AuspicianteResponse.model_validate(auspiciante)


@router.put("/api/v1/auspiciantes/{auspiciante_id}", response_model=AuspicianteResponse)
def update_auspiciante_endpoint(
    auspiciante_id: str,
    body: AuspicianteUpdate,
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    auspiciante = update_auspiciante(db, uuid.UUID(auspiciante_id), body)
    return AuspicianteResponse.model_validate(auspiciante)


@router.delete("/api/v1/auspiciantes/{auspiciante_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_auspiciante_endpoint(
    auspiciante_id: str,
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    delete_auspiciante(db, uuid.UUID(auspiciante_id))


@router.get("/api/v1/boletines/{boletin_id}/auspiciantes", response_model=list[AuspicianteResponse])
def get_boletin_auspiciantes_endpoint(
    boletin_id: str,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    auspiciantes = get_auspiciantes_by_boletin(db, uuid.UUID(boletin_id))
    return [AuspicianteResponse.model_validate(a) for a in auspiciantes]


@router.put("/api/v1/boletines/{boletin_id}/auspiciantes", response_model=list[AuspicianteResponse])
def update_boletin_auspiciantes_endpoint(
    boletin_id: str,
    body: BoletinAuspiciantesRequest,
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    auspiciantes = update_boletin_auspiciantes(db, uuid.UUID(boletin_id), body.auspiciantes_ids)
    return [AuspicianteResponse.model_validate(a) for a in auspiciantes]
