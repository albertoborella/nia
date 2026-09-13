import uuid
import os
import json
import re
from datetime import datetime, timezone

from sqlmodel import Session, select, func

from app.models.prompt import Prompt
from app.schemas.prompt import PromptCreate, PromptUpdate
from app.utils.errors import NotFoundError, ValidationError
from app.services.ia_response_parser import parse_incidents_response


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "responses")


def create_prompt(db: Session, data: PromptCreate, user_id: uuid.UUID) -> Prompt:
    prompt = Prompt(
        nombre=data.nombre,
        descripcion=data.descripcion,
        template=data.template,
        tipo=data.tipo,
        activo=True,
        configuracion=data.configuracion or {},
        creado_por=user_id,
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


def list_prompts(
    db: Session, page: int = 1, limit: int = 20, tipo: str | None = None, activo: bool | None = None
) -> tuple[list[Prompt], int]:
    query = select(Prompt)
    count_query = select(func.count()).select_from(Prompt)

    if tipo:
        query = query.where(Prompt.tipo == tipo)
        count_query = count_query.where(Prompt.tipo == tipo)

    if activo is not None:
        query = query.where(Prompt.activo == activo)
        count_query = count_query.where(Prompt.activo == activo)

    total = db.exec(count_query).one()
    offset = (page - 1) * limit
    prompts = db.exec(query.order_by(Prompt.fecha_creacion.desc()).offset(offset).limit(limit)).all()

    return list(prompts), total


def get_prompt_by_id(db: Session, prompt_id: uuid.UUID) -> Prompt:
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise NotFoundError("Prompt", str(prompt_id))
    return prompt


def update_prompt(db: Session, prompt_id: uuid.UUID, data: PromptUpdate) -> Prompt:
    prompt = get_prompt_by_id(db, prompt_id)
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(prompt, key, value)

    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


def delete_prompt(db: Session, prompt_id: uuid.UUID) -> None:
    prompt = get_prompt_by_id(db, prompt_id)
    db.delete(prompt)
    db.commit()


def render_prompt(db: Session, prompt_id: uuid.UUID, variables: dict) -> dict:
    prompt = get_prompt_by_id(db, prompt_id)
    
    template = prompt.template
    pattern = r"\{\{(\w+)\}\}"
    placeholders = re.findall(pattern, template)
    
    missing = [p for p in placeholders if p not in variables]
    if missing:
        raise ValidationError(
            code="PROMPT_MISSING_VARIABLES",
            message=f"Missing required variables: {', '.join(missing)}"
        )
    
    rendered = template
    for key, value in variables.items():
        rendered = rendered.replace("{{" + key + "}}", str(value))
    
    return {
        "prompt_id": prompt.id,
        "nombre": prompt.nombre,
        "rendered_text": rendered,
        "variables": variables
    }


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def upload_ai_response(
    db: Session, 
    prompt_id: uuid.UUID, 
    boletin_id: uuid.UUID, 
    response_data: list[dict], 
    rendered_prompt: str
) -> dict:
    valid_incidents, validation_errors = parse_incidents_response(response_data)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    response_dir = os.path.join(DATA_DIR, str(prompt_id), str(boletin_id), timestamp)
    _ensure_dir(response_dir)
    
    with open(os.path.join(response_dir, "prompt_rendered.txt"), "w", encoding="utf-8") as f:
        f.write(rendered_prompt)
    
    with open(os.path.join(response_dir, "response.json"), "w", encoding="utf-8") as f:
        json.dump(response_data, f, ensure_ascii=False, indent=2)
    
    return {
        "total_received": len(response_data),
        "total_stored": len(valid_incidents),
        "errors": validation_errors,
        "response_path": response_dir
    }
