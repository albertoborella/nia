import uuid
from pydantic import BaseModel, ConfigDict


class AuspicianteCreate(BaseModel):
    nombre: str
    logo_url: str | None = None
    enlace: str | None = None
    descripcion: str | None = None


class AuspicianteUpdate(BaseModel):
    nombre: str | None = None
    logo_url: str | None = None
    enlace: str | None = None
    descripcion: str | None = None
    activo: bool | None = None


class AuspicianteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str
    logo_url: str | None
    enlace: str | None
    descripcion: str | None
    activo: bool


class AuspicianteListResponse(BaseModel):
    items: list[AuspicianteResponse]
    total: int
    page: int
    limit: int


class BoletinAuspiciantesRequest(BaseModel):
    auspiciantes_ids: list[uuid.UUID]
