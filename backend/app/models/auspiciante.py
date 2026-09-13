import uuid

from sqlmodel import SQLModel, Field


class Auspiciante(SQLModel, table=True):
    __tablename__ = "auspiciantes"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    nombre: str = Field(max_length=255, nullable=False)
    logo_url: str | None = Field(default=None, max_length=1000)
    enlace: str | None = Field(default=None, max_length=1000)
    descripcion: str | None = Field(default=None)
    activo: bool = Field(default=True)


class BoletinAuspiciante(SQLModel, table=True):
    __tablename__ = "boletin_auspiciantes"

    boletin_id: uuid.UUID = Field(foreign_key="boletines.id", primary_key=True)
    auspiciante_id: uuid.UUID = Field(foreign_key="auspiciantes.id", primary_key=True)
