import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.database import get_db
from app.middleware.auth import get_current_user, require_director
from app.models.usuario import Usuario
from app.schemas.incidente import (
    IncidenteCreate,
    IncidenteUpdate,
    IncidenteResponse,
    IncidenteListResponse,
    IncidenteImportRequest,
    IncidenteImportResult,
    ArticuloGenerateRequest,
    ArticuloResponse,
    ArticuloUpdateRequest,
)
from app.services.incidente_service import (
    create_incidente,
    list_incidentes,
    get_incidente_by_id,
    update_incidente,
    delete_incidente,
    import_from_stored_response,
    generar_articulo,
    get_articulo,
    update_articulo,
)

router = APIRouter(prefix="/api/v1/incidentes", tags=["incidentes"])


@router.get("", response_model=IncidenteListResponse)
def list_incidentes_endpoint(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    pais: str | None = Query(None),
    riesgo: str | None = Query(None),
    estado_verificacion: str | None = Query(None),
    boletin_asignado: str | None = Query(None),
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    boletin_uuid = uuid.UUID(boletin_asignado) if boletin_asignado else None
    incidentes, total = list_incidentes(
        db,
        page=page,
        limit=limit,
        pais=pais,
        riesgo=riesgo,
        estado_verificacion=estado_verificacion,
        boletin_asignado=boletin_uuid,
    )
    items = [IncidenteResponse.model_validate(i) for i in incidentes]
    return IncidenteListResponse(items=items, total=total, page=page, limit=limit)


@router.post("", response_model=IncidenteResponse, status_code=status.HTTP_201_CREATED)
def create_incidente_endpoint(
    body: IncidenteCreate,
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    incidente = create_incidente(db, body, user.id)
    return IncidenteResponse.model_validate(incidente)


@router.get("/{incidente_id}", response_model=IncidenteResponse)
def get_incidente_endpoint(
    incidente_id: str,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    incidente = get_incidente_by_id(db, uuid.UUID(incidente_id))
    return IncidenteResponse.model_validate(incidente)


@router.put("/{incidente_id}", response_model=IncidenteResponse)
def update_incidente_endpoint(
    incidente_id: str,
    body: IncidenteUpdate,
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    incidente = update_incidente(db, uuid.UUID(incidente_id), body)
    return IncidenteResponse.model_validate(incidente)


@router.delete("/{incidente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incidente_endpoint(
    incidente_id: str,
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    delete_incidente(db, uuid.UUID(incidente_id))


@router.post("/importar", response_model=IncidenteImportResult)
def importar_incidentes_endpoint(
    prompt_id: str = Query(...),
    boletin_id: str = Query(...),
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    result = import_from_stored_response(db, uuid.UUID(prompt_id), uuid.UUID(boletin_id), user.id)
    return IncidenteImportResult(**result)


@router.post("/{boletin_id}/generar-articulo", response_model=ArticuloResponse)
def generar_articulo_endpoint(
    boletin_id: str,
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    result = generar_articulo(db, uuid.UUID(boletin_id))
    return ArticuloResponse(**result)


@router.get("/{boletin_id}/articulo", response_model=ArticuloResponse)
def get_articulo_endpoint(
    boletin_id: str,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = get_articulo(db, uuid.UUID(boletin_id))
    return ArticuloResponse(**result)


@router.put("/{boletin_id}/articulo", response_model=ArticuloResponse)
def update_articulo_endpoint(
    boletin_id: str,
    body: ArticuloUpdateRequest,
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    result = update_articulo(db, uuid.UUID(boletin_id), body)
    return ArticuloResponse(**result)
