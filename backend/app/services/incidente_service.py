import uuid
import os
import json
from datetime import datetime, timezone, date

from sqlmodel import Session, select, func

from app.models.incidente import Incidente
from app.models.boletin import Boletin
from app.schemas.incidente import IncidenteCreate, IncidenteUpdate, ArticuloUpdateRequest
from app.utils.errors import NotFoundError, ValidationError, ConflictError
from app.services.ia_response_parser import parse_incidents_response
from app.services.articulo_generator import generate_markdown_article

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "responses")
ARTICULOS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "articulos")

VALID_RIESGO = {"alto", "medio", "bajo"}
VALID_SEVERIDAD = {"critico", "alto", "medio", "bajo"}
VALID_ESTADO_VERIFICACION = {"confirmado", "en_investigacion", "descartado"}
VALID_ESTADO_EDITORIAL = {"generado", "revisado", "aprobado", "incluido"}


def _validate_incidente_data(data: IncidenteCreate | IncidenteUpdate) -> None:
    if isinstance(data, IncidenteCreate):
        if data.riesgo not in VALID_RIESGO:
            raise ValidationError(
                code="INVALID_RIESGO",
                message=f"Invalid riesgo '{data.riesgo}'. Valid values: {', '.join(sorted(VALID_RIESGO))}",
            )
        if data.severidad not in VALID_SEVERIDAD:
            raise ValidationError(
                code="INVALID_SEVERIDAD",
                message=f"Invalid severidad '{data.severidad}'. Valid values: {', '.join(sorted(VALID_SEVERIDAD))}",
            )
    else:
        if data.riesgo is not None and data.riesgo not in VALID_RIESGO:
            raise ValidationError(
                code="INVALID_RIESGO",
                message=f"Invalid riesgo '{data.riesgo}'. Valid values: {', '.join(sorted(VALID_RIESGO))}",
            )
        if data.severidad is not None and data.severidad not in VALID_SEVERIDAD:
            raise ValidationError(
                code="INVALID_SEVERIDAD",
                message=f"Invalid severidad '{data.severidad}'. Valid values: {', '.join(sorted(VALID_SEVERIDAD))}",
            )
        if data.estado_verificacion is not None and data.estado_verificacion not in VALID_ESTADO_VERIFICACION:
            raise ValidationError(
                code="INVALID_ESTADO_VERIFICACION",
                message=f"Invalid estado_verificacion '{data.estado_verificacion}'. Valid values: {', '.join(sorted(VALID_ESTADO_VERIFICACION))}",
            )
        if data.estado_editorial is not None and data.estado_editorial not in VALID_ESTADO_EDITORIAL:
            raise ValidationError(
                code="INVALID_ESTADO_EDITORIAL",
                message=f"Invalid estado_editorial '{data.estado_editorial}'. Valid values: {', '.join(sorted(VALID_ESTADO_EDITORIAL))}",
            )


def create_incidente(db: Session, data: IncidenteCreate, user_id: uuid.UUID) -> Incidente:
    _validate_incidente_data(data)

    incidente = Incidente(
        incidente=data.incidente,
        producto=data.producto,
        patogeno=data.patogeno,
        organismo=data.organismo,
        pais=data.pais,
        riesgo=data.riesgo,
        fecha_inicio=data.fecha_inicio,
        fecha_cierre=data.fecha_cierre,
        observaciones=data.observaciones,
        texto_noticia=data.texto_noticia,
        fuente_url=data.fuente_url,
        fuente_nombre=data.fuente_nombre,
        fecha_consulta=data.fecha_consulta,
        estado_verificacion=data.estado_verificacion,
        estado_editorial=data.estado_editorial,
        severidad=data.severidad,
        boletin_asignado=data.boletin_asignado,
        creado_por=user_id,
    )
    db.add(incidente)
    db.commit()
    db.refresh(incidente)
    return incidente


def list_incidentes(
    db: Session,
    page: int = 1,
    limit: int = 20,
    pais: str | None = None,
    riesgo: str | None = None,
    estado_verificacion: str | None = None,
    boletin_asignado: uuid.UUID | None = None,
) -> tuple[list[Incidente], int]:
    query = select(Incidente)
    count_query = select(func.count()).select_from(Incidente)

    if pais:
        query = query.where(Incidente.pais == pais)
        count_query = count_query.where(Incidente.pais == pais)
    if riesgo:
        query = query.where(Incidente.riesgo == riesgo)
        count_query = count_query.where(Incidente.riesgo == riesgo)
    if estado_verificacion:
        query = query.where(Incidente.estado_verificacion == estado_verificacion)
        count_query = count_query.where(Incidente.estado_verificacion == estado_verificacion)
    if boletin_asignado:
        query = query.where(Incidente.boletin_asignado == boletin_asignado)
        count_query = count_query.where(Incidente.boletin_asignado == boletin_asignado)

    total = db.exec(count_query).one()
    offset = (page - 1) * limit
    incidentes = db.exec(query.order_by(Incidente.fecha_creacion.desc()).offset(offset).limit(limit)).all()

    return list(incidentes), total


def get_incidente_by_id(db: Session, incidente_id: uuid.UUID) -> Incidente:
    incidente = db.query(Incidente).filter(Incidente.id == incidente_id).first()
    if not incidente:
        raise NotFoundError("Incidente", str(incidente_id))
    return incidente


def update_incidente(db: Session, incidente_id: uuid.UUID, data: IncidenteUpdate) -> Incidente:
    incidente = get_incidente_by_id(db, incidente_id)
    _validate_incidente_data(data)

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(incidente, key, value)

    db.add(incidente)
    db.commit()
    db.refresh(incidente)
    return incidente


def delete_incidente(db: Session, incidente_id: uuid.UUID) -> None:
    incidente = get_incidente_by_id(db, incidente_id)
    db.delete(incidente)
    db.commit()


def import_from_stored_response(
    db: Session, prompt_id: uuid.UUID, boletin_id: uuid.UUID, user_id: uuid.UUID
) -> dict:
    prompt_dir = os.path.join(DATA_DIR, str(prompt_id), str(boletin_id))
    if not os.path.exists(prompt_dir):
        raise NotFoundError("Response directory", prompt_dir)

    timestamp_dirs = sorted(
        [d for d in os.listdir(prompt_dir) if os.path.isdir(os.path.join(prompt_dir, d))],
        reverse=True,
    )
    if not timestamp_dirs:
        raise NotFoundError("Response files in", prompt_dir)

    latest_dir = os.path.join(prompt_dir, timestamp_dirs[0])
    response_file = os.path.join(latest_dir, "response.json")
    if not os.path.exists(response_file):
        raise NotFoundError("response.json in", latest_dir)

    with open(response_file, "r", encoding="utf-8") as f:
        response_data = json.load(f)

    valid_incidents, validation_errors = parse_incidents_response(response_data)

    imported = 0
    for inc_data in valid_incidents:
        try:
            incidente = Incidente(
                incidente=inc_data.get("incidente", ""),
                producto=inc_data.get("producto", ""),
                patogeno=inc_data.get("patogeno", ""),
                organismo=inc_data.get("organismo"),
                pais=inc_data.get("pais", ""),
                riesgo=inc_data.get("riesgo", "medio"),
                fecha_inicio=date.fromisoformat(inc_data["fecha_inicio"]) if inc_data.get("fecha_inicio") else date.today(),
                fecha_cierre=date.fromisoformat(inc_data["fecha_cierre"]) if inc_data.get("fecha_cierre") else None,
                observaciones=inc_data.get("observaciones"),
                texto_noticia=inc_data.get("texto_noticia"),
                fuente_url=inc_data.get("fuente_url"),
                fuente_nombre=inc_data.get("fuente_nombre"),
                fecha_consulta=date.fromisoformat(inc_data["fecha_consulta"]) if inc_data.get("fecha_consulta") else date.today(),
                estado_verificacion=inc_data.get("estado_verificacion", "confirmado"),
                estado_editorial=inc_data.get("estado_editorial", "generado"),
                severidad=inc_data.get("severidad", "medio"),
                boletin_asignado=boletin_id,
                creado_por=user_id,
            )
            db.add(incidente)
            imported += 1
        except Exception as e:
            validation_errors.append({"error": str(e), "data": inc_data})

    db.commit()

    return {"total_imported": imported, "errors": validation_errors}


def get_incidentes_by_boletin(db: Session, boletin_id: uuid.UUID) -> list[Incidente]:
    incidentes = db.exec(
        select(Incidente).where(Incidente.boletin_asignado == boletin_id)
    ).all()
    return list(incidentes)


def generar_articulo(db: Session, boletin_id: uuid.UUID) -> dict:
    boletin = db.query(Boletin).filter(Boletin.id == boletin_id).first()
    if not boletin:
        raise NotFoundError("Boletin", str(boletin_id))

    incidentes = get_incidentes_by_boletin(db, boletin_id)
    if not incidentes:
        raise ValidationError(
            code="NO_INCIDENTS",
            message=f"No incidents found for boletin {boletin_id}",
        )

    markdown = generate_markdown_article(incidentes, boletin.nombre)

    articulo_dir = os.path.join(ARTICULOS_DIR, str(boletin_id))
    os.makedirs(articulo_dir, exist_ok=True)

    articulo_path = os.path.join(articulo_dir, "articulo.md")
    with open(articulo_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    return {
        "articulo_markdown": markdown,
        "version": 1,
        "incidentes_incluidos": len(incidentes),
        "fecha_generacion": datetime.now(timezone.utc),
    }


def get_articulo(db: Session, boletin_id: uuid.UUID) -> dict:
    boletin = db.query(Boletin).filter(Boletin.id == boletin_id).first()
    if not boletin:
        raise NotFoundError("Boletin", str(boletin_id))

    articulo_path = os.path.join(ARTICULOS_DIR, str(boletin_id), "articulo.md")
    if not os.path.exists(articulo_path):
        raise NotFoundError("Articulo for boletin", str(boletin_id))

    with open(articulo_path, "r", encoding="utf-8") as f:
        markdown = f.read()

    incidentes = get_incidentes_by_boletin(db, boletin_id)

    return {
        "articulo_markdown": markdown,
        "version": 1,
        "incidentes_incluidos": len(incidentes),
        "fecha_generacion": datetime.fromtimestamp(os.path.getmtime(articulo_path), tz=timezone.utc),
    }


def update_articulo(db: Session, boletin_id: uuid.UUID, data: ArticuloUpdateRequest) -> dict:
    boletin = db.query(Boletin).filter(Boletin.id == boletin_id).first()
    if not boletin:
        raise NotFoundError("Boletin", str(boletin_id))

    articulo_dir = os.path.join(ARTICULOS_DIR, str(boletin_id))
    os.makedirs(articulo_dir, exist_ok=True)

    articulo_path = os.path.join(articulo_dir, "articulo.md")
    with open(articulo_path, "w", encoding="utf-8") as f:
        f.write(data.articulo_markdown)

    incidentes = get_incidentes_by_boletin(db, boletin_id)

    return {
        "articulo_markdown": data.articulo_markdown,
        "version": data.version,
        "incidentes_incluidos": len(incidentes),
        "fecha_generacion": datetime.now(timezone.utc),
    }
