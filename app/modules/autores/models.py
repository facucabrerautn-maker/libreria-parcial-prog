from typing import Optional, List

from sqlmodel import Field

from app.core.base import BaseModel


class Autor(BaseModel, table=True):
    __tablename__ = "autor"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True)
    nacionalidad: Optional[str] = None

    # La relación con Libro a través de LibroAutor se completa en C-07
