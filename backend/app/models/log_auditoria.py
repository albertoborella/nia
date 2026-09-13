import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field


class LogAuditoria(SQLModel, table=True):
    __tablename__ = "log_auditoria"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    usuario_id: uuid.UUID | None = Field(default=None, foreign_key="usuarios.id")
    accion: str = Field(max_length=100, nullable=False)
    entidad_tipo: str = Field(max_length=50, nullable=False)
    entidad_id: uuid.UUID | None = Field(default=None)
    detalles: dict = Field(default={}, sa_column=Column(JSON))
    fecha: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ip: str | None = Field(default=None, max_length=45)
