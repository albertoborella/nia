import uuid
from datetime import datetime, date, timezone

from sqlmodel import SQLModel, Field


class Incidente(SQLModel, table=True):
    __tablename__ = "incidentes"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    incidente: str = Field(max_length=500, nullable=False)
    producto: str = Field(max_length=255, nullable=False)
    patogeno: str = Field(max_length=255, nullable=False)
    organismo: str | None = Field(default=None, max_length=255)
    pais: str = Field(max_length=100, nullable=False)
    riesgo: str = Field(max_length=10, nullable=False)
    fecha_inicio: date = Field(nullable=False)
    fecha_cierre: date | None = Field(default=None)
    observaciones: str | None = Field(default=None)
    texto_noticia: str | None = Field(default=None)
    fuente_url: str | None = Field(default=None, max_length=1000)
    fuente_nombre: str | None = Field(default=None, max_length=500)
    fecha_consulta: date = Field(nullable=False)
    estado_verificacion: str = Field(max_length=20, nullable=False, default="confirmado")
    estado_editorial: str = Field(max_length=20, nullable=False, default="generado")
    severidad: str = Field(max_length=10, nullable=False)
    boletin_asignado: uuid.UUID | None = Field(default=None, foreign_key="boletines.id")
    creado_por: uuid.UUID | None = Field(default=None, foreign_key="usuarios.id")
    fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
