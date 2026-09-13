import uuid
from datetime import datetime, date, timezone

from sqlmodel import SQLModel, Field


class Boletin(SQLModel, table=True):
    __tablename__ = "boletines"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    nombre: str = Field(max_length=255, nullable=False)
    periodo_inicio: date = Field(nullable=False)
    periodo_fin: date = Field(nullable=False)
    fecha_publicacion_estimada: date | None = Field(default=None)
    estado: str = Field(max_length=20, nullable=False, default="borrador")
    creado_por: uuid.UUID | None = Field(default=None, foreign_key="usuarios.id")
    fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    fecha_cierre: datetime | None = Field(default=None)
