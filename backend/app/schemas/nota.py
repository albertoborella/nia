import uuid
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict


class NotaUpdate(BaseModel):
    titulo: str | None = None
    autor: str | None = None
    fuente: str | None = None
    tema: str | None = None


class NotaEstadoUpdate(BaseModel):
    estado: str
    boletin_asignado: uuid.UUID | None = None
    observaciones: str | None = None


class NotaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    titulo: str
    autor: str
    colaborador_id: uuid.UUID | None
    fuente: str | None
    tema: str | None
    archivo_url: str
    archivo_tipo: str
    estado: str
    boletin_asignado: uuid.UUID | None
    fecha_recepcion: date
    fecha_revision: date | None
    revisado_por: uuid.UUID | None
    observaciones: str | None


class NotaListResponse(BaseModel):
    items: list[NotaResponse]
    total: int
    page: int
    limit: int
