import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field


class Seccion(SQLModel, table=True):
    __tablename__ = "secciones"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    boletin_id: uuid.UUID = Field(foreign_key="boletines.id", nullable=False)
    tipo: str = Field(max_length=30, nullable=False)
    orden: int = Field(nullable=False)
    estado: str = Field(max_length=20, nullable=False, default="pendiente")
    contenido: dict = Field(default={}, sa_column=Column(JSON))
    completado_por: uuid.UUID | None = Field(default=None, foreign_key="usuarios.id")
    fecha_completado: datetime | None = Field(default=None)
