import uuid
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    nombre: str = Field(max_length=255, nullable=False)
    email: str = Field(max_length=255, unique=True, nullable=False, index=True)
    password_hash: str = Field(max_length=255, nullable=False)
    rol: str = Field(max_length=20, nullable=False)
    activo: bool = Field(default=True)
    fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ultimo_acceso: datetime | None = Field(default=None)
