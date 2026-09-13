import uuid
from datetime import datetime, date, timezone

from sqlmodel import SQLModel, Field


class Nota(SQLModel, table=True):
    __tablename__ = "notas_colaboradores"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    titulo: str = Field(max_length=500, nullable=False)
    autor: str = Field(max_length=255, nullable=False)
    colaborador_id: uuid.UUID | None = Field(default=None, foreign_key="usuarios.id")
    fuente: str | None = Field(default=None, max_length=500)
    tema: str | None = Field(default=None, max_length=100)
    archivo_url: str = Field(max_length=1000, nullable=False)
    archivo_tipo: str = Field(max_length=10, nullable=False)
    estado: str = Field(max_length=20, nullable=False, default="pendiente")
    boletin_asignado: uuid.UUID | None = Field(default=None, foreign_key="boletines.id")
    fecha_recepcion: date = Field(nullable=False)
    fecha_revision: date | None = Field(default=None)
    revisado_por: uuid.UUID | None = Field(default=None, foreign_key="usuarios.id")
    observaciones: str | None = Field(default=None)
