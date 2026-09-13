import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.database import get_db
from app.middleware.auth import get_current_user, require_director
from app.models.usuario import Usuario
from app.schemas.prompt import (
    PromptCreate,
    PromptUpdate,
    PromptResponse,
    PromptListResponse,
    PromptRenderRequest,
    PromptRenderResponse,
    PromptResponseUpload,
    UploadResult,
)
from app.services.prompt_service import (
    create_prompt,
    list_prompts,
    get_prompt_by_id,
    update_prompt,
    delete_prompt,
    render_prompt,
    upload_ai_response,
)

router = APIRouter(prefix="/api/v1/prompts", tags=["prompts"])


@router.get("", response_model=PromptListResponse)
def list_prompts_endpoint(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    tipo: str | None = Query(None),
    activo: bool | None = Query(None),
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prompts, total = list_prompts(db, page=page, limit=limit, tipo=tipo, activo=activo)
    items = [PromptResponse.model_validate(p) for p in prompts]
    return PromptListResponse(items=items, total=total, page=page, limit=limit)


@router.post("", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
def create_prompt_endpoint(
    body: PromptCreate,
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    prompt = create_prompt(db, body, user.id)
    return PromptResponse.model_validate(prompt)


@router.get("/{prompt_id}", response_model=PromptResponse)
def get_prompt_endpoint(
    prompt_id: str,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prompt = get_prompt_by_id(db, uuid.UUID(prompt_id))
    return PromptResponse.model_validate(prompt)


@router.put("/{prompt_id}", response_model=PromptResponse)
def update_prompt_endpoint(
    prompt_id: str,
    body: PromptUpdate,
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    prompt = update_prompt(db, uuid.UUID(prompt_id), body)
    return PromptResponse.model_validate(prompt)


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt_endpoint(
    prompt_id: str,
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    delete_prompt(db, uuid.UUID(prompt_id))


@router.post("/{prompt_id}/render", response_model=PromptRenderResponse)
def render_prompt_endpoint(
    prompt_id: str,
    body: PromptRenderRequest,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = render_prompt(db, uuid.UUID(prompt_id), body.variables)
    return PromptRenderResponse(**result)


@router.post("/{prompt_id}/upload-response", response_model=UploadResult)
def upload_response_endpoint(
    prompt_id: str,
    body: PromptResponseUpload,
    boletin_id: str = Query(...),
    user: Usuario = Depends(require_director),
    db: Session = Depends(get_db),
):
    get_prompt_by_id(db, uuid.UUID(prompt_id))
    
    rendered_text = body.prompt_rendered or ""
    
    result = upload_ai_response(
        db,
        uuid.UUID(prompt_id),
        uuid.UUID(boletin_id),
        body.incidentes,
        rendered_text
    )
    return UploadResult(**result)
