import uuid
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict


class IncidenteCreate(BaseModel):
    incidente: str
    producto: str
    patogeno: str
    organismo: str | None = None
    pais: str
    riesgo: str
    fecha_inicio: date
    fecha_cierre: date | None = None
    observaciones: str | None = None
    texto_noticia: str | None = None
    fuente_url: str | None = None
    fuente_nombre: str | None = None
    fecha_consulta: date
    estado_verificacion: str = "confirmado"
    estado_editorial: str = "generado"
    severidad: str
    boletin_asignado: uuid.UUID | None = None


class IncidenteUpdate(BaseModel):
    incidente: str | None = None
    producto: str | None = None
    patogeno: str | None = None
    organismo: str | None = None
    pais: str | None = None
    riesgo: str | None = None
    fecha_inicio: date | None = None
    fecha_cierre: date | None = None
    observaciones: str | None = None
    texto_noticia: str | None = None
    fuente_url: str | None = None
    fuente_nombre: str | None = None
    fecha_consulta: date | None = None
    estado_verificacion: str | None = None
    estado_editorial: str | None = None
    severidad: str | None = None
    boletin_asignado: uuid.UUID | None = None


class IncidenteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incidente: str
    producto: str
    patogeno: str
    organismo: str | None
    pais: str
    riesgo: str
    fecha_inicio: date
    fecha_cierre: date | None
    observaciones: str | None
    texto_noticia: str | None
    fuente_url: str | None
    fuente_nombre: str | None
    fecha_consulta: date
    estado_verificacion: str
    estado_editorial: str
    severidad: str
    boletin_asignado: uuid.UUID | None
    creado_por: uuid.UUID | None
    fecha_creacion: datetime


class IncidenteListResponse(BaseModel):
    items: list[IncidenteResponse]
    total: int
    page: int
    limit: int


class IncidenteImportRequest(BaseModel):
    prompt_id: uuid.UUID
    boletin_id: uuid.UUID


class IncidenteImportResult(BaseModel):
    total_imported: int
    errors: list[dict]


class ArticuloGenerateRequest(BaseModel):
    pass


class ArticuloResponse(BaseModel):
    articulo_markdown: str
    version: int
    incidentes_incluidos: int
    fecha_generacion: datetime


class ArticuloUpdateRequest(BaseModel):
    articulo_markdown: str
    version: int
