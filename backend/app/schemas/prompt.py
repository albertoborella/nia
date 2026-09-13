import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PromptCreate(BaseModel):
    nombre: str
    descripcion: str | None = None
    template: str
    tipo: str
    configuracion: dict | None = None


class PromptUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    template: str | None = None
    tipo: str | None = None
    activo: bool | None = None
    configuracion: dict | None = None


class PromptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str
    descripcion: str | None
    template: str
    tipo: str
    activo: bool
    configuracion: dict
    creado_por: uuid.UUID | None
    fecha_creacion: datetime


class PromptListResponse(BaseModel):
    items: list[PromptResponse]
    total: int
    page: int
    limit: int


class PromptRenderRequest(BaseModel):
    variables: dict


class PromptRenderResponse(BaseModel):
    prompt_id: uuid.UUID
    nombre: str
    rendered_text: str
    variables: dict


class IncidentResponse(BaseModel):
    incidente: str
    producto: str | None = None
    patogeno: str | None = None
    organismo: str | None = None
    pais: str | None = None
    riesgo: str | None = None
    fecha_inicio: str | None = None
    fecha_fin: str | None = None
    fuente: str | None = None
    detalles: str | None = None


class PromptResponseUpload(BaseModel):
    incidentes: list[dict]
    prompt_rendered: str | None = None


class UploadResult(BaseModel):
    total_received: int
    total_stored: int
    errors: list[dict]
