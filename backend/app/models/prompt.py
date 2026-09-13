import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field


class Prompt(SQLModel, table=True):
    __tablename__ = "prompts"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    nombre: str = Field(max_length=255, nullable=False)
    descripcion: str | None = Field(default=None)
    template: str = Field(nullable=False)
    tipo: str = Field(max_length=30, nullable=False)
    activo: bool = Field(default=True)
    configuracion: dict = Field(default={}, sa_column=Column(JSON, default={}))
    creado_por: uuid.UUID | None = Field(default=None, foreign_key="usuarios.id")
    fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
