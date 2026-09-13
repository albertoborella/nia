from pydantic import BaseModel


class SeccionUpdate(BaseModel):
    contenido: dict
