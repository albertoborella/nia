import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LogAuditoriaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    usuario_id: uuid.UUID | None
    accion: str
    entidad_tipo: str
    entidad_id: uuid.UUID | None
    detalles: dict
    fecha: datetime
    ip: str | None


class LogAuditoriaListResponse(BaseModel):
    items: list[LogAuditoriaResponse]
    total: int
    page: int
    limit: int
