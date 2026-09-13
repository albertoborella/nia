import uuid
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict


class BoletinCreate(BaseModel):
    nombre: str
    periodo_inicio: date
    periodo_fin: date
    fecha_publicacion_estimada: date | None = None


class BoletinUpdate(BaseModel):
    nombre: str | None = None
    periodo_inicio: date | None = None
    periodo_fin: date | None = None
    fecha_publicacion_estimada: date | None = None


class SeccionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tipo: str
    orden: int
    estado: str
    contenido: dict
    completado_por: uuid.UUID | None
    fecha_completado: datetime | None


class BoletinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str
    periodo_inicio: date
    periodo_fin: date
    fecha_publicacion_estimada: date | None
    estado: str
    creado_por: uuid.UUID | None
    fecha_creacion: datetime
    fecha_cierre: datetime | None
    secciones: list[SeccionResponse] = []
    progreso: int = 0


class BoletinListResponse(BaseModel):
    items: list[BoletinResponse]
    total: int
    page: int
    limit: int


class CompletarSeccionRequest(BaseModel):
    tipo: str


class TablaIncidentesRequest(BaseModel):
    incidentes_ids: list[uuid.UUID]
    orden: list[uuid.UUID]


class AuspiciantesBoletinRequest(BaseModel):
    auspiciantes_ids: list[uuid.UUID]


class NotaAsignarRequest(BaseModel):
    nota_ids: list[uuid.UUID]


class NotaDesasignarRequest(BaseModel):
    nota_ids: list[uuid.UUID]


class NotaBoletinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    titulo: str
    autor: str
    tema: str | None
    archivo_tipo: str
    estado: str
    fecha_recepcion: date
    boletin_asignado: uuid.UUID | None


class NotaBoletinListResponse(BaseModel):
    items: list[NotaBoletinResponse]
    total: int
