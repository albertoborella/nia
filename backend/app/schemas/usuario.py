import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UsuarioCreate(BaseModel):
    nombre: str
    email: str
    password: str
    rol: str


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    email: str | None = None
    rol: str | None = None
    activo: bool | None = None


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str
    email: str
    rol: str
    activo: bool
    fecha_creacion: datetime
    ultimo_acceso: datetime | None


class UsuarioListResponse(BaseModel):
    items: list[UsuarioResponse]
    total: int
    page: int
    limit: int
