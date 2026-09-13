import uuid
from datetime import date, timezone
from pathlib import Path

from fastapi import UploadFile
from sqlmodel import Session, select, func

from app.models.nota import Nota
from app.schemas.nota import NotaUpdate, NotaEstadoUpdate
from app.utils.errors import NotFoundError, ValidationError, ConflictError

UPLOAD_DIR = Path("uploads/notas")
VALID_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"}
VALID_STATES = {"pendiente", "aprobada", "archivada"}
VALID_TRANSITIONS = {
    "pendiente": {"aprobada", "archivada"},
    "aprobada": {"archivada"},
}


def _validate_file_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in VALID_EXTENSIONS:
        raise ValidationError(
            code="INVALID_FILE_TYPE",
            message=f"File type '{ext}' is not allowed. Allowed types: .pdf, .doc, .docx, .txt, .rtf, .odt",
        )
    return ext


def _get_upload_path(user_id: uuid.UUID, filename: str) -> Path:
    ext = Path(filename).suffix.lower()
    dir_path = UPLOAD_DIR / str(user_id)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path / f"{uuid.uuid4()}{ext}"


def create_nota(
    db: Session,
    titulo: str,
    autor: str,
    archivo: UploadFile,
    user_id: uuid.UUID,
    fuente: str | None = None,
    tema: str | None = None,
) -> Nota:
    ext = _validate_file_extension(archivo.filename)
    file_path = _get_upload_path(user_id, archivo.filename)

    import shutil
    with open(file_path, "wb") as f:
        shutil.copyfileobj(archivo.file, f)

    nota = Nota(
        titulo=titulo,
        autor=autor,
        fuente=fuente,
        tema=tema,
        archivo_url=str(file_path),
        archivo_tipo=ext.lstrip("."),
        estado="pendiente",
        colaborador_id=user_id,
        fecha_recepcion=date.today(),
    )
    db.add(nota)
    db.commit()
    db.refresh(nota)
    return nota


def list_notas(
    db: Session,
    page: int = 1,
    limit: int = 20,
    estado: str | None = None,
    tema: str | None = None,
    autor: str | None = None,
) -> tuple[list[Nota], int]:
    query = select(Nota)
    count_query = select(func.count()).select_from(Nota)

    if estado:
        query = query.where(Nota.estado == estado)
        count_query = count_query.where(Nota.estado == estado)
    if tema:
        query = query.where(Nota.tema == tema)
        count_query = count_query.where(Nota.tema == tema)
    if autor:
        query = query.where(Nota.autor.ilike(f"%{autor}%"))
        count_query = count_query.where(Nota.autor.ilike(f"%{autor}%"))

    total = db.exec(count_query).one()
    offset = (page - 1) * limit
    notas = db.exec(query.order_by(Nota.fecha_recepcion.desc()).offset(offset).limit(limit)).all()

    return list(notas), total


def get_nota_by_id(db: Session, nota_id: uuid.UUID) -> Nota:
    nota = db.query(Nota).filter(Nota.id == nota_id).first()
    if not nota:
        raise NotFoundError("Nota", str(nota_id))
    return nota


def update_nota(db: Session, nota_id: uuid.UUID, data: NotaUpdate) -> Nota:
    nota = get_nota_by_id(db, nota_id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(nota, key, value)
    db.add(nota)
    db.commit()
    db.refresh(nota)
    return nota


def delete_nota(db: Session, nota_id: uuid.UUID) -> None:
    nota = get_nota_by_id(db, nota_id)

    file_path = Path(nota.archivo_url)
    if file_path.exists():
        file_path.unlink()

    db.delete(nota)
    db.commit()


def update_nota_estado(
    db: Session,
    nota_id: uuid.UUID,
    data: NotaEstadoUpdate,
    user_id: uuid.UUID,
) -> Nota:
    nota = get_nota_by_id(db, nota_id)

    if data.estado not in VALID_STATES:
        raise ValidationError(
            code="INVALID_STATE",
            message=f"Invalid state '{data.estado}'. Valid states: {', '.join(sorted(VALID_STATES))}",
        )

    allowed = VALID_TRANSITIONS.get(nota.estado, set())
    if data.estado not in allowed:
        raise ConflictError(
            f"Cannot transition from '{nota.estado}' to '{data.estado}'"
        )

    nota.estado = data.estado
    nota.fecha_revision = date.today()
    nota.revisado_por = user_id
    if data.boletin_asignado is not None:
        nota.boletin_asignado = data.boletin_asignado
    if data.observaciones is not None:
        nota.observaciones = data.observaciones

    db.add(nota)
    db.commit()
    db.refresh(nota)
    return nota


def get_nota_file_path(db: Session, nota_id: uuid.UUID) -> tuple[Path, str]:
    nota = get_nota_by_id(db, nota_id)
    file_path = Path(nota.archivo_url)
    if not file_path.exists():
        raise NotFoundError("Nota file", str(nota_id))
    media_types = {
        "pdf": "application/pdf",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "txt": "text/plain",
        "rtf": "application/rtf",
        "odt": "application/vnd.oasis.opendocument.text",
    }
    media_type = media_types.get(nota.archivo_tipo, "application/octet-stream")
    return file_path, media_type
